package io.datawire;

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Handler;

public class Closer extends BaseDatawireHandler {
    public Closer(Handler delegate, TestHandler closer) {
        add(delegate);
        add(closer);
    }
    @Override
    public void onConnectionBound(Event e) {
        e.delegate();
        e.redispatch(TestEvent.Type.OPENED, this);
    }
    @Override
    public void onConnectionUnbound(Event e) {
        e.delegate();
        e.redispatch(TestEvent.Type.CLOSED, this);
    }
}
