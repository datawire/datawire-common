package io.datawire;

import io.datawire.impl.EventImpl;

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.EventType;

public class BaseTestHandler extends BaseDatawireHandler implements TestHandler {

    @Override
    public void handle(Event e) {
        EventType type = e.getEventType();
        if (type instanceof TestEvent.Type) {
            switch((TestEvent.Type) type) {
            case OPENED:
                onOpened(e);
                break;
            case CLOSED:
                onClosed(e);
                break;
            case NOT_A_TEST_TYPE:
                throw new IllegalArgumentException("Cannot dispatch an invalid type value");

            // default: Do not add default, so that compiler warns for unhandled events!
            }
        } else {
            super.handle(e);
        }
    }

    @Override
    public void onOpened(Event e) { onUnhandled(e); }

    @Override
    public void onClosed(Event e) { onUnhandled(e); }

}
