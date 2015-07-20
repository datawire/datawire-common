package io.datawire;

import org.apache.qpid.proton.reactor.FlowController;
import org.apache.qpid.proton.reactor.Handshaker;

public class Processor extends BaseHandler {

    private final org.apache.qpid.proton.engine.Handler delegate;
    public Processor(org.apache.qpid.proton.engine.Handler delegate, int window) {
        this.delegate = delegate != null ? delegate : this;
        add(new FlowController(window));
        add(new Handshaker());
        add(new Decoder(delegate));
    }

    public Processor(org.apache.qpid.proton.engine.Handler delegate) {
        this(delegate, 1024);
    }

    public Processor(int window) {
        this(null, window);
    }

    public Processor() {
        this(null);
    }

    @Override
    public void onUnhandled(org.apache.qpid.proton.engine.Event event) {
        if (delegate == this || event.getConnection() == null)
            return;
        event.dispatch(delegate);
    }
}
