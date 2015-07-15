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
    
    public static final Object MESSAGE = new Object();
    
    private org.apache.qpid.proton.engine.Event impl;

    public EventImpl(org.apache.qpid.proton.engine.Event e) {
        impl = e;
    }

    public Record attachments() {
        return impl.attachments();
    }

    public EventType getType() {
        return impl.getType();
    }

    public org.apache.qpid.proton.engine.Event.Type getBuiltinType() {
        return impl.getBuiltinType();
    }

    public Object getContext() {
        return impl.getContext();
    }

    public void dispatch(Handler handler) throws HandlerException {
        impl.dispatch(handler);
    }

    public Connection getConnection() {
        return impl.getConnection();
    }

    public Session getSession() {
        return impl.getSession();
    }

    public Link getLink() {
        return impl.getLink();
    }

    public Delivery getDelivery() {
        return impl.getDelivery();
    }

    public Transport getTransport() {
        return impl.getTransport();
    }

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
        Message m = impl.attachments().get(MESSAGE, Message.class);
        return m;                
    }

  
}
