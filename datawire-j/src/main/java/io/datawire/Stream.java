package io.datawire;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.logging.Logger;

import io.datawire.impl.TransientStore;

import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.amqp.messaging.Section;
import org.apache.qpid.proton.amqp.messaging.Terminus;
import org.apache.qpid.proton.amqp.transport.Target;
import org.apache.qpid.proton.engine.Delivery;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Extendable;
import org.apache.qpid.proton.engine.ExtendableAccessor;
import org.apache.qpid.proton.engine.Record;
import org.apache.qpid.proton.engine.Sender;
import org.apache.qpid.proton.engine.Link;
import org.apache.qpid.proton.engine.Receiver;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.FlowController;
import org.apache.qpid.proton.reactor.Handshaker;
import org.apache.qpid.proton.reactor.Reactor;

/**
 * A stream is an event handler that holds a customizable {@link Store}
 * representing a linear sequence of messages, the stream will
 * collect messages from any incoming links into the store, and
 * broadcast anything in the store to all outgoing links
 * 
 * <ul>
 * <li>
 * by supplying the stream as the {@link Receivers}'s event handler, we
 * can locally establish incoming links to pull messages into
 * the stream
 * <li>
 * likewise, by supplying the stream as the {@link Sender}'s event
 * handler, we can locally establish outgoing links to push
 * messages out of the stream
 * <li>
 * by supplying the stream as the event handler for incoming
 * connections ({@link Reactor#acceptor(String, int, Handler)}), we can collect any messages that are sent to us
 * into the stream's message store
 * </ul>
 */
public class Stream extends BaseDatawireHandler {
    private static final Logger log = Logger.getLogger(Stream.class.getName());
    public static final ExtendableAccessor<Sender, Reader> SENDER_READER = new ExtendableAccessor<>(Reader.class);

    private Store store;
    private final ArrayList<Receiver> incoming;
    private final ArrayList<Sender> outgoing;
    private Message message;
    private boolean closed;
    private int queued;
    public Stream() {
        this (new TransientStore());
    }
    public Stream(Store store) {
        this.store = store;
        add(new FlowController());
        add(new Handshaker());
        add(new Decoder());
        incoming = new ArrayList<>();
        outgoing = new ArrayList<>();
        message = Message.Factory.create();
        message.setAddress(null);
        closed = false;
    }

    public void put(Message msg) {
        store.put(msg, msg.getAddress());
    }

    public void put(Object body) {
        if (body instanceof Message) {
            put((Message)body);
        } else {
            if (body instanceof Section) {
                message.setBody((Section)body);
            } else {
                message.setBody(new AmqpValue(body));
            }
            put(message);
        }
    }

    public void close() {
        closed = true;
    }

    @Override
    public void onLinkLocalOpen(Event e) {
        setup(e);
    }

    @Override
    public void onLinkRemoteOpen(Event e) {
        setup(e);
    }

    private void setup(Event e) {
        Sender sender = e.getSender();
        if (sender != null && SENDER_READER.get(sender) == null) {
            String rsa = sender.getRemoteSource() != null ? sender.getRemoteSource().getAddress() : null;
            String lsa = sender.getSource() != null ? sender.getSource().getAddress() : null;
            String rta = sender.getRemoteTarget() != null ? sender.getRemoteTarget().getAddress() : null;
            String lta = sender.getTarget() != null ? sender.getTarget().getAddress() : null;
            Reader reader = store.reader(
                    rsa != null ? rsa : lsa != null ? lsa : rta != null ? rta : lta );
            SENDER_READER.set(sender, reader);
            outgoing.add(sender);
            return;
        }
        Receiver receiver = e.getReceiver();
        if (receiver != null && !incoming.contains(receiver)) {
            incoming.add(receiver);
        }
    }

    @Override
    public void onLinkFinal(Event e) {
        Sender sender = e.getSender();
        if (sender != null) {
            Reader reader = SENDER_READER.get(sender);
            reader.close();
            SENDER_READER.set(sender, null);
            outgoing.remove(sender);
        } else {
            incoming.remove(e.getReceiver());
        }
    }

    @Override
    public void onLinkFlow(Event e) {
        Sender sender = e.getSender();
        if (sender != null) {
            pump(sender);
        }
    }
    private void pump(Sender sender) {
        Reader reader = SENDER_READER.get(sender);
        while (reader.more() && sender.getCredit() > 0 && sender.getQueued() < 1024) {
            Entry entry = reader.next();
            DatawireUtils.send(sender, entry.getEncodedMessage());
        }
        if (!reader.more()) {
            sender.drained();
            if (closed) {
                sender.close();
            }
        }
    }

    private void pump() {
        queued = 0;
        for (Sender sender : outgoing) {
            pump(sender);
            queued += sender.getQueued();
        }
        store.gc();
        store.flush();
    }

    @Override
    public void onReactorQuiesced(Event e) {
        pump();
    }

    @Override
    public void onEncodedMessage(DatawireEvent e) {
        Receiver receiver = e.getReceiver();
        ByteBuffer buffer = e.getEncodedMessage();
        String address = receiver.getTarget().getAddress();
        store.put(buffer, address);
    }
    
    private boolean matches(String host, String port, String address, Link link) {
        if (host == null) {
            return false;
        } else {
            if (port == null)
                throw new IllegalArgumentException("Port must be specified if host is specified");
            if (address == null)
                throw new IllegalArgumentException("Address must be specified if host is specified");
            String terminusAddress;
            if (link instanceof Sender) {
                terminusAddress = link.getTarget().getAddress();
            } else {
                terminusAddress = link.getSource().getAddress();
            }
            String hostname = link.getSession().getConnection().getHostname();
            return (hostname.equals(String.format("%s:%s", host, port))
                    && address.equals(terminusAddress));
        }
    }

    /**
     * force reconnect of all stream participants that do not match the specified criteria???
     * @param sender
     * @param receiver
     * @param host
     * @param port
     * @param address
     */
    public void relink(boolean sender, boolean receiver, String host, String port, String address) {
        if (sender) {
            for (Sender l : outgoing) {
                if (matches(host, port, address, l)) {
                    log.fine("omitting spurious relink");
                } else {
                    io.datawire.Link.RELINK_FLAG.set(l, true);
                    l.close();
                }
            }
        }
        if (receiver) {
            for (Receiver l : incoming) {
                if (matches(host, port, address, l)) {
                    log.fine("Omitting spurious relink");
                } else {
                    io.datawire.Link.RELINK_FLAG.set(l, true);
                    l.close();
                }
            }
        }
    }
}