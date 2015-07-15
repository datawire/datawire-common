package io.datawire.impl;

import io.datawire.Event;
import io.datawire.Handler;

public class DatawireEventTypeImpl {

    public static void dispatch(Event.Type type,
            org.apache.qpid.proton.engine.Event e, org.apache.qpid.proton.engine.Handler h) {
        Handler handler;
        if (h instanceof Handler) {
            handler = (Handler) h;
        } else {
            h.onUnhandled(e);
            return;
        }
        Event event;
        if (e instanceof Event) {
            event = (Event) e;
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
