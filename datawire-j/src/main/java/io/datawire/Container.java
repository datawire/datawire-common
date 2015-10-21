/**
 * Copyright 2015 datawire. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package io.datawire;

import java.util.AbstractCollection;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.NoSuchElementException;

import org.apache.qpid.proton.engine.BaseHandler;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.reactor.Handshaker;
import org.apache.qpid.proton.reactor.Reactor;

/**
 * Container is a handler that maintains a map of address -> handler
 * <p>
 * For any established {@link org.apache.qpid.proton.engine.Link} the
 * <code>Container</code> will select the most specific address prefix of the
 * registered nodes and associate the node as the handler for that link. For
 * {@link org.apache.qpid.proton.engine.Sender} links the address will be the
 * remote source address and for {@link org.apache.qupid.proton.engine.Receiver}
 * links the address will be the remote target address.
 */
public class Container extends BaseDatawireHandler {

    /**
     * @param address
     *            link address of the form
     *            <code>[&lt;path&gt;][?&lt;query&gt;]</code>
     * @return a collection of address path prefixes ordered from longest to
     *         shortest. A null address yields a collection with one null
     *         element.
     */
    public static Collection<String> ancestors(String address) {
        if (address == null) {
            return Collections.singleton(address);
        } else {
            final String path = address.split("\\?", 2)[0];
            // need to pre-calculate cutlist as AbstractCollection requires
            // size().
            final ArrayList<Integer> cutlist = new ArrayList<>();
            int off = 0;
            for (String part : path.split("/", -1)) {
                int partend = off + part.length();
                if (partend > off || off == 0) {
                    cutlist.add(partend);
                }
                int partslash = partend + 1;
                cutlist.add(partslash);
                off = partslash;
            }
            cutlist.remove(cutlist.size() - 1);
            return new AbstractCollection<String>() {

                @Override
                public Iterator<String> iterator() {
                    return new Iterator<String>() {
                        int last = cutlist.size() - 1;

                        @Override
                        public boolean hasNext() {
                            return last >= 0;
                        }

                        @Override
                        public String next() {
                            if (!hasNext()) {
                                throw new NoSuchElementException();
                            }
                            return path.substring(0, cutlist.get(last--));
                        }

                        @Override
                        public void remove() {
                            throw new UnsupportedOperationException();
                        }
                    };
                }

                @Override
                public int size() {
                    return cutlist.size();
                }
            };
        }
    }

    private final Handler root;
    // TODO: replace with a trie
    private final Map<String, Handler> nodes = new HashMap<>();
    private final ArrayList<Link> links = new ArrayList<>();

    /**
     * Construct a container
     *
     * @param root
     *            The default node for the root of the address namespace
     */
    public Container(Handler root) {
        if (root == null) {
            throw new NullPointerException("root must be non-null");
        }
        this.root = root;
        add(new Handshaker());
    }

    /**
     * Add a handler node at the specified address or prefix
     *
     * @param address
     *            Address or prefix for links
     * @param node
     */
    public void put(String address, Handler node) {
        if (node == null) {
            throw new NullPointerException("node must be non-null");
        }
        nodes.put(address, node);
    }

    /**
     * @param address
     *            or prefix to find
     * @return the most specific registered node or the root node if no match is
     *         found
     * @see #Container(Handler)
     * @see #put(String, Handler)
     */
    Handler get(String address) {
        for (String prefix : ancestors(address)) {
            Handler node = nodes.get(prefix);
            if (node != null) {
                return node;
            }
        }
        return root;
    }

    private void link(String address, Link.Config config) {
        if (config.handlers.size() == 0) {
            Handler node = get(address);
            if (node != null)
                config.handlers.add(node);
        }
    }

    private void lateStart(Link link) {
        // XXX: links created after container.start() do not get started...
    }

    public class SenderBuilder extends Sender.SenderBuilder {
        SenderBuilder() {
        }

        @Override
        public Sender create() {
            link(config().source, config());
            Sender sender = super.create();
            links.add(sender);
            lateStart(sender);
            return sender;
        }
    }

    /**
     * @return a {@link SenderBuilder} for the {@link Sender} associated with
     *         this Container
     */
    public SenderBuilder sender() {
        return new SenderBuilder();
    }

    /**
     * a helper method to build a sender used for jython binding
     *
     * @param target
     *            sender target address
     * @param source
     *            sender source address
     * @param handlers
     *            additional handlers
     * @return a {@link Sender}
     */
    public Sender sender(String target, String source, Handler... handlers) {
        return sender().withTarget(target).withSource(source)
                .withHandlers(handlers).create();
    }

    public class ReceiverBuilder extends Receiver.ReceiverBuilder {
        ReceiverBuilder() {
        }

        @Override
        public Receiver create() {
            link(config().target, config());
            Receiver receiver = super.create();
            links.add(receiver);
            lateStart(receiver);
            return receiver;
        }
    }

    /**
     * @return a {@link ReceiverBuilder} for creating a {@link Receiver}
     *         associated with this Container
     */
    public ReceiverBuilder receiver() {
        return new ReceiverBuilder();
    }

    /**
     * @param source
     *            receiver source address
     * @param target
     *            receiver target address
     * @param drain
     *            receiver drain flag, see
     *            {@link ReceiverBuilder#withDrain(boolean)}
     * @param handlers
     *            additional receiver handlers
     * @return a {@link Receiver}
     */
    public Receiver receiver(String source, String target, boolean drain,
            Handler... handlers) {
        return receiver().withSource(source).withTarget(target)
                .withDrain(drain).withHandlers(handlers).create();
    }

    /**
     * Start the container and all the links <br>
     * XXX: this has no impact on links managed on incoming connections?
     *
     * @param reactor
     */
    public void start(Reactor reactor) {
        for (Link l : links) {
            l.start(reactor);
        }
    }

    /**
     * Stop the container and all the links <br>
     * XXX: this has no impact on links managed on incoming connections?
     *
     * @param reactor
     */
    public void stop(Reactor reactor) {
        for (Link l : links) {
            l.stop(reactor);
        }
    }

    @Override
    public void onLinkRemoteOpen(Event e) {
        org.apache.qpid.proton.engine.Link link = e.getLink();
        final String address;
        if (link instanceof org.apache.qpid.proton.engine.Sender) {
            address = link.getRemoteSource().getAddress();
        } else {
            address = link.getRemoteTarget().getAddress();
        }
        Handler node = get(address);
        if (node != null) {
            BaseHandler.setHandler(link, node);
            e.dispatch(node);
        }
    }

    @Override
    public void onReactorQuiesced(Event e) {
        e.dispatch(root);
        for (Handler node : nodes.values()) {
            e.dispatch(node);
        }
    }

    @Override
    public void onTransportClosed(Event e) {
        e.getConnection().free();
    }
}
