/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import java.nio.BufferOverflowException;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.Queue;

import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.amqp.messaging.Section;
import org.apache.qpid.proton.engine.Delivery;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Session;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.Reactor;

/**
 * @author bozzo
 *
 */
public class Sender extends Link {
    
    private final Config config;
    private Queue<ByteBuffer> buffer = new LinkedList<ByteBuffer>();
    private Message message =  Message.Factory.create();
    private boolean closed = false;

    static class Config extends Link.Config {
        // no fields
    }

    public abstract static class Builder<S extends Sender, C extends Config, B extends Builder<S, C, B>> extends Link.Builder<S, C, B> {
        // no fields
    }


    static class SenderBuilder extends Builder<Sender, Config, SenderBuilder> {
        private Config config = new Config();
        @Override protected Config config() { return config; }
        @Override protected SenderBuilder self() { return this; }
        @Override 
        public Sender create() {
            Config config = this.config;
            this.config = null;
            return new Sender(config);
        }
    }

    public static Builder<?,?,?> Builder() {
        return new SenderBuilder();
    }

    private static Config validate(Config config) {
        if (config.target == null) {
            throw new IllegalArgumentException("Target is required");
        }
        return config;
    }

    protected Sender(Config config) {
        super(validate(config));
        this.config = config;
    }

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
            Delivery dlv = sender.delivery(deliveryTag());
            ByteBuffer bytes = buffer.poll();
            bytes.flip();
            sender.send(bytes.array(), bytes.position(), bytes.limit());
            dlv.settle();
        }
        if (closed && buffer.isEmpty()) {
            sender.close();
        }
    }

    private int tag = 1;
    protected byte[] deliveryTag() {
        return String.valueOf(tag++).getBytes();
    }

    public void send(Object o) {
        if (get_link() == null) {
            throw new IllegalStateException("link is not started");
        }
        if (o instanceof Message) {
            Message msg = (Message) o;
            buffer.add(encode(msg));
        } else if ( o instanceof Section ) {
            message.setBody((Section) o);
            send(message);
        } else {
            message.setBody(new AmqpValue(o));
            send(message);
        }
    }

    public void close() {
        closed = true;
    }

    private ByteBuffer encode(Message msg) {
        int size = 1000;
        while(true) {
            try {
                byte[] bytes = new byte[size];
                int length = msg.encode(bytes, 0, size);
                return ByteBuffer.wrap(bytes, length, size-length);
            } catch (BufferOverflowException ex) {
                size *= 2;
                continue; 
            }
        }
    }
}
