package io.datawire;

public class BaseHandler extends org.apache.qpid.proton.engine.BaseHandler implements Handler {

    @Override
    public void onMessage(io.datawire.Event e) { onUnhandled(e); }

}
