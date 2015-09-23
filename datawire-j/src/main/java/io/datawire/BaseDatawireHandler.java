/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import io.datawire.impl.EventImpl;

import org.apache.qpid.proton.engine.EventType;

/**
 * Default implementation of all {@link DatawireHandler} methods. Use this class as the
 * base for your handlers.
 *
 * @author bozzo
 *
 */
public class BaseDatawireHandler extends org.apache.qpid.proton.engine.BaseHandler
        implements DatawireHandler {

    @Override
    public void handle(org.apache.qpid.proton.engine.Event e) {
        EventType type = e.getEventType();
        if (type instanceof DatawireEvent.Type) {
            final DatawireEvent event;
            if (e instanceof DatawireEvent) {
                event = (DatawireEvent) e;
            } else {
                event = new EventImpl(e);
            }
            switch((DatawireEvent.Type) type) {
            case ENCODED_MESSAGE:
                onEncodedMessage(event);
                break;
            case MESSAGE:
                onMessage(event);
                break;
            case DRAINED:
                onDrained(event);
                break;
            case SAMPLE:
                onSample(event);
                break;
            case NOT_A_DATAWIRE_TYPE:
                throw new IllegalArgumentException("Cannot dispatch an invalid type value");

            // default: Do not add default, so that compiler warns for unhandled events!
            }
        } else {
            super.handle(e);
        }
    }

    @Override
    public void onEncodedMessage(DatawireEvent e) {
        onUnhandled(e);
    }

    @Override
    public void onMessage(DatawireEvent e) {
        onUnhandled(e);
    }

    @Override
    public void onSample(DatawireEvent e) {
        onUnhandled(e);
    }

    @Override
    public void onDrained(DatawireEvent e) {
        onUnhandled(e);
    }

}
