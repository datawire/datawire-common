package io.datawire.impl;

import org.apache.qpid.proton.engine.Connection;
import org.apache.qpid.proton.engine.Delivery;
import org.apache.qpid.proton.engine.EventType;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.HandlerException;
import org.apache.qpid.proton.engine.Link;
import org.apache.qpid.proton.engine.Receiver;
import org.apache.qpid.proton.engine.Record;
import org.apache.qpid.proton.engine.Sender;
import org.apache.qpid.proton.engine.Session;
import org.apache.qpid.proton.engine.Transport;
import org.apache.qpid.proton.engine.impl.RecordImpl;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.Reactor;
import org.apache.qpid.proton.reactor.Selectable;
import org.apache.qpid.proton.reactor.Task;

import io.datawire.DatawireEvent;

public class EventImpl implements DatawireEvent {

    private org.apache.qpid.proton.engine.Event impl;

    public EventImpl(org.apache.qpid.proton.engine.Event e) {
        impl = e;
    }

    @Override
    public Record attachments() {
        return impl.attachments();
    }

    @Override
    public EventType getEventType() {
        return impl.getEventType();
    }

    @Override
    public org.apache.qpid.proton.engine.Event.Type getType() {
        return impl.getType();
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
    public Sender getSender() {
        return impl.getSender();
    }

    @Override
    public Receiver getReceiver() {
        return impl.getReceiver();
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
        EventType type = impl.getEventType();
        if (type instanceof Type)
            return (Type)type;
        return Type.NOT_A_DATAWIRE_TYPE;
    }

    @Override
    public Message getMessage() {
        Message m = MESSAGE_ACCESSOR.get(impl);
        return m;
    }

    @Override
    public void delegate() throws HandlerException {
        impl.delegate();
    }

}
