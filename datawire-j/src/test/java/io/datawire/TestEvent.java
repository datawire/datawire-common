package io.datawire;

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.EventType;
import org.apache.qpid.proton.engine.Handler;

public interface TestEvent extends DatawireEvent {
    public enum Type implements EventType {
        OPENED,
        CLOSED,
        NOT_A_TEST_TYPE {
            @Override
            public boolean isValid() {
                return false;
            }
        };
        @Override
        public void dispatch(Event e, Handler h) {
            TestHandler handler;
            if (h instanceof TestHandler) {
                handler = (TestHandler) h;
            } else {
                h.onUnhandled(e);
                return;
            }
            switch(this) {
            case OPENED:
                handler.onOpened(e);
                break;
            case CLOSED:
                handler.onClosed(e);
                break;
            case NOT_A_TEST_TYPE:
                throw new IllegalArgumentException("Cannot dispatch an invalid type value");

            // default: Do not add default, so that compiler warns for unhandled events!
            }
        }

        @Override
        public boolean isValid() {
            return true;
        }
    }
}
