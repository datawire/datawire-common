package io.datawire;

import org.apache.qpid.proton.engine.EventType;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.message.Message;


public interface Event extends org.apache.qpid.proton.engine.Event {

    public enum Type implements EventType {
        MESSAGE,
        SAMPLE,
        NOT_A_DATAWIRE_TYPE;

        @Override
        public void dispatch(org.apache.qpid.proton.engine.Event e, Handler h) {
            io.datawire.impl.DatawireEventTypeImpl.dispatch(this, e, h);
            
        }

        @Override
        public boolean isValid() {
            return this != NOT_A_DATAWIRE_TYPE;
        }
    }
    
    Type getDatawireType();
    
    Message getMessage();
}
