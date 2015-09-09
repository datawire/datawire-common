package io.datawire;

import org.apache.qpid.proton.reactor.Reactor;
import org.apache.qpid.proton.reactor.Task;

public class Timeout extends BaseDatawireHandler {

    private Task timer;
    private boolean cancelled = false;

    public void setTimeout(Reactor reactor, int timeout) {
        if (timer != null)
            throw new IllegalArgumentException("Timeout is already set");
        timer = reactor.schedule(timeout, this);
        cancelled  = false;
    }
    
    public void cancel() {
        if (timer == null)
            throw new IllegalArgumentException("Cannot cancel when timeout is not set");
        timer.cancel();
        timer = null;
        cancelled = true;
    }
    
    public boolean isCancelled() { return cancelled; }
}
