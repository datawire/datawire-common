package io.datawire;

import org.apache.qpid.proton.engine.Event;

public interface TestHandler extends DatawireHandler {
    void onOpened(Event e);
    void onClosed(Event e);
}
