/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.Queue;

import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.amqp.messaging.Section;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Session;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.Reactor;

/**
 * Handler for managing a {@link org.apache.qpid.proton.engine.Sender}
 * <p>
 * If you need to manage many senders you can use a {@link Linker}
 * @author bozzo
 *
 */
public class Sender extends Link {
    
    private final Config config;
    private Queue<ByteBuffer> buffer = new LinkedList<ByteBuffer>();
    private Message message =  Message.Factory.create();
    private boolean closed = false;

    /**
     * Configuration for a {@link Sender}.
     * <p>
     * A sender must have a valid {@link Link.Config#target}
     * @author bozzo
     *
     */
    static class Config extends Link.Config {
        // no fields
    }

    public abstract static class Builder<S extends Sender, C extends Config, B extends Builder<S, C, B>> extends Link.Builder<S, C, B> {
        // no fields
    }

    /**
     * A builder for the {@link Sender}.
     * @author bozzo
     *
     */
    static class SenderBuilder extends Builder<Sender, Config, SenderBuilder> {
        private Config config = new Config();
        @Override protected Config config() { return config; }
        @Override protected SenderBuilder self() { return this; }
        /**
         * Create the {@link Sender} as configured. The builder instance is not usable after this call.
         */
        @Override 
        public Sender create() {
            Config config = this.config;
            this.config = null;
            return new Sender(config);
        }
    }

    /**
     * @return a new {@link SenderBuilder}
     */
    public static Builder<?,?,?> Builder() {
        return new SenderBuilder();
    }

    private static Config validate(Config config) {
        if (config.target == null) {
            throw new IllegalArgumentException("Target is required");
        }
        return config;
    }

    private Sender(Config config) {
        super(validate(config));
        this.config = config;
    }

    /**
     * Reference constructor
     * @param target Sender target address, mandatory
     * @param source Sender source address, optional
     * @param handlers Child handlers for the link
     */
    public Sender(String target, String source, Handler... handlers) {
        super(handlers);
        config = new Config();
        config.target = target;
        config.source = source;
        config.handlers.addAll(Arrays.asList(handlers));
        validate(config);
    }

    private final LinkCreator link = new LinkCreator() {
        @Override
        public org.apache.qpid.proton.engine.Link create(Reactor reactor) {
            Session session = _session(reactor);
            org.apache.qpid.proton.engine.Sender snd = session.sender(String.format("%1s->%2s", config.source, config.target));
            setLinkSource(snd, config.source);
            setLinkTarget(snd, config.target);
            return snd;
        }
    };

    @Override
    protected LinkCreator getLinkCreator() {
        return link ;
    }

    /**
     * Target network address
     */
    @Override
    protected String getNetwork() {
        return new Address(config.target).getNetwork();
    }

    @Override
    public void onLinkFlow(Event event) {
        __pump(event.getLink());
        super.onLinkFlow(event);
    }

    private void __pump(org.apache.qpid.proton.engine.Link link2) {
        final org.apache.qpid.proton.engine.Sender sender;
        if (link2 instanceof org.apache.qpid.proton.engine.Sender) {
            sender = (org.apache.qpid.proton.engine.Sender) link2;
        } else {
            throw new IllegalArgumentException("Expected a sender");
        }
        while (!buffer.isEmpty() && sender.getCredit() > 0) {
            ByteBuffer bytes = buffer.poll();
            DatawireUtils.send(sender, tag, bytes);
        }
        if (closed && buffer.isEmpty()) {
            sender.close();
        }
    }

    private SimpleTag tag = new SimpleTag(1);

    /**
     * Send the specified message
     * @param msg The message to send
     */
    public void send(Message msg) {
        if (getLink() == null) {
            throw new IllegalStateException("link is not started");
        }
        buffer.add(DatawireUtils.encode(msg));
    }

    /**
     * Send a message with the specified body
     * @param body The body of the message
     */
    public void send(Section body) {
        message.setBody(body);
        send(message);
    }

    /**
     * Send a message with the specified object as the body
     * @param value The value to send as the message body
     */
    public void send(Object value) {
        if (value instanceof Message) {
            send((Message)value);
        } else if (value instanceof Section) {
            send((Section)value);
        } else {
            message.setBody(new AmqpValue(value));
            send(message);
        }
    }

    /**
     * Close the link after sending all pending messages
     */
    public void close() {
        closed = true;
        // XXX: missing __pump() ?
    }
}
