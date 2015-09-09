package io.datawire;

import org.apache.qpid.proton.engine.Event;

public class BaseTestHandler extends BaseDatawireHandler implements TestHandler {

    @Override
    public void onOpened(Event e) { onUnhandled(e); }

    @Override
    public void onClosed(Event e) { onUnhandled(e); }

}
