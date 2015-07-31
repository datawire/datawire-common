package io.datawire.impl;

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Handler;

import io.datawire.DatawireEvent;
import io.datawire.DatawireHandler;

public class DatawireEventTypeImpl {

    public static void dispatch(DatawireEvent.Type type, Event e, Handler h) {
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
        case DRAINED:
            handler.onDrained(event);
            break;
        case SAMPLE:
            handler.onSample(event);
            break;
        case NOT_A_DATAWIRE_TYPE:
            throw new IllegalArgumentException("Cannot dispatch an invalid type value");

        // default: Do not add default, so that compiler warns for unhandled events!
        }
    }

    private static EventImpl makeEvent(Event e) {
        // TODO: refactor pool from collector
        return new EventImpl(e);
    }

}
