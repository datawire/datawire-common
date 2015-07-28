package io.datawire.impl;

import org.apache.qpid.proton.engine.Connection;
import org.apache.qpid.proton.engine.Delivery;
import org.apache.qpid.proton.engine.EventType;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.HandlerException;
import org.apache.qpid.proton.engine.Link;
import org.apache.qpid.proton.engine.Record;
import org.apache.qpid.proton.engine.Session;
import org.apache.qpid.proton.engine.Transport;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.Reactor;
import org.apache.qpid.proton.reactor.Selectable;
import org.apache.qpid.proton.reactor.Task;

import io.datawire.Event;

public class EventImpl implements Event {
    public static class MessageAccessor {
        public Message get(Record record) {
            return record.get(this, Message.class);
        }
    }
    
    public static final MessageAccessor MESSAGE = new MessageAccessor();
    
    private org.apache.qpid.proton.engine.Event impl;

    public EventImpl(org.apache.qpid.proton.engine.Event e) {
        impl = e;
    }

    @Override
    public Record attachments() {
        return impl.attachments();
    }

    @Override
    public EventType getType() {
        return impl.getType();
    }

    @Override
    public org.apache.qpid.proton.engine.Event.Type getBuiltinType() {
        return impl.getBuiltinType();
    }

    @Override
    public Object getContext() {
        return impl.getContext();
    }

    @Override
    public void dispatch(Handler handler) throws HandlerException {
        impl.dispatch(handler);
    }

    @Override
    public void redispatch(EventType as_type, Handler handler) {
        impl.redispatch(as_type, handler);
    }

    @Override
    public Connection getConnection() {
        return impl.getConnection();
    }

    @Override
    public Session getSession() {
        return impl.getSession();
    }

    @Override
    public Link getLink() {
        return impl.getLink();
    }

    @Override
    public Delivery getDelivery() {
        return impl.getDelivery();
    }

    @Override
    public Transport getTransport() {
        return impl.getTransport();
    }

    @Override
    public Reactor getReactor() {
        return impl.getReactor();
    }

    public Selectable getSelectable() {
        return impl.getSelectable();
    }

    public Task getTask() {
        return impl.getTask();
    }

    public org.apache.qpid.proton.engine.Event copy() {
        return impl.copy();
    }

    @Override
    public Type getDatawireType() {
        EventType type = impl.getType();
        if (type instanceof Type)
            return (Type)type;
        return Type.NOT_A_DATAWIRE_TYPE;
    }

    @Override
    public Message getMessage() {
        Message m = MESSAGE.get(impl.attachments());
        return m;                
    }

    @Override
    public void delegate() throws HandlerException {
        impl.delegate();
    }
}
