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
        public boolean isValid() {
            return true;
        }
    }
}
