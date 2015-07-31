package io.datawire.impl;

import io.datawire.DatawireEvent;
import io.datawire.DatawireHandler;

public class DatawireEventTypeImpl {

    public static void dispatch(DatawireEvent.Type type,
            org.apache.qpid.proton.engine.Event e, org.apache.qpid.proton.engine.Handler h) {
        DatawireHandler handler;
        if (h instanceof DatawireHandler) {
            handler = (DatawireHandler) h;
        } else {
            h.onUnhandled(e);
            return;
        }
        DatawireEvent event;
        if (e instanceof DatawireEvent) {
            event = (DatawireEvent) e;
        } else {
            event = makeEvent(e);
        }
        switch(type) {
        case MESSAGE:
            handler.onMessage(event);
            break;
        case NOT_A_DATAWIRE_TYPE:
            throw new IllegalArgumentException("Cannot dispatch an invalid type value");
       
        }
    }

    private static EventImpl makeEvent(org.apache.qpid.proton.engine.Event e) {
        // TODO: refactor pool from collector
        return new EventImpl(e);
    }

}
