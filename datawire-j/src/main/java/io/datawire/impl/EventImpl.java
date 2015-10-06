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
package io.datawire.impl;

import java.nio.ByteBuffer;

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
    public Handler getRootHandler() {
        return impl.getRootHandler();
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
    public ByteBuffer getEncodedMessage() {
        Delivery delivery = getDelivery();
        if (delivery == null) {
            return null;
        }
        ByteBuffer b = ENCODED_MESSAGE_ACCESSOR.get(delivery);
        return b;
    }

    @Override
    public void delegate() throws HandlerException {
        impl.delegate();
    }

}
