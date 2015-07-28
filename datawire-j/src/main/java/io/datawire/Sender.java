/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

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
    
    private String target;
    private String source;
    private Queue<byte[]> __buffer = new LinkedList<byte[]>();
    private byte[] __data = new byte[512];
    private Message __message =  Message.Factory.create();
    private boolean __closed = false;

    public Sender(String target, Handler... handlers) {
        this(target, null, handlers);
    }

    public Sender(String target, String source, Handler... handlers) {
        super(handlers);
        this.target = target;
        this.source = source;
    }

    private final LinkCreator link = new LinkCreator() {
        @Override
        public org.apache.qpid.proton.engine.Link create(Reactor reactor) {
            Session session = _session(reactor);
            org.apache.qpid.proton.engine.Sender snd = session.sender(String.format("%1s->%2s", source, target));
            setLinkSource(snd, source);
            setLinkTarget(snd, target);
            return snd;
        }
    };

    @Override
    protected LinkCreator getLinkCreator() {
        return link ;
    }

    @Override
    protected String getNetwork() {
        return new Address(target).getNetwork();
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
        while (!__buffer.isEmpty() && sender.getCredit() > 0) {
            Delivery dlv = sender.delivery(deliveryTag());
            byte[] bytes = __buffer.poll();
            sender.send(bytes, 0, bytes.length);
            dlv.settle();
        }
        if (__closed && __buffer.isEmpty()) {
            sender.close();
        }
    }
    
    private int tag = 1;
    private byte[] deliveryTag() {
        return String.valueOf(tag++).getBytes();
    }

    public void send(Object o) {
        if (get_link() == null) {
            throw new IllegalStateException("link is not started");
        }
        if (o instanceof Message) {
            Message msg = (Message) o;
            __buffer.add(encode(msg));
        } else if ( o instanceof Section ) {
            __message.setBody((Section) o);
            send(__message);
        } else {
            __message.setBody(new AmqpValue(o));
            send(__message);
        }
    }

    private byte[] encode(Message msg) {
        int len = msg.encode(__data, 0, __data.length);
        // XXX: __data resizing
        return Arrays.copyOf(__data, len);
    }
    
    public void close() {
        __closed = true;
    }
}
