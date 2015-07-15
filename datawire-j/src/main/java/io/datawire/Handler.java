package io.datawire;



public interface Handler extends org.apache.qpid.proton.engine.Handler {
    public void onMessage(Event e);
}
