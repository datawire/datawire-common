/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import org.apache.qpid.proton.reactor.FlowController;
import org.apache.qpid.proton.reactor.Handshaker;

/**
 * A handler for processing incoming messages. It aggregates a {@link FlowController}, a {@link Handshaker} and a {@link Decoder}. 
 * <p>
 * 
 * <pre>
 * {@code
 * class MyHandler extends BaseHandler {
 *   {@literal @}Override
 *   public void onMessage(Event e) {
 *     // process message
 *   }
 *   
 *   public static void main(String[] args) {
 *     Reactor r = Reactor.Factory.create();
 *     r.acceptor("localhost", "12345", new Processor(new MyHandler()));
 *     r.run();
 *   }
 * }
 * }
 * </pre>
 * <p>
 * 
 * @author bozzo
 *
 */
public class Processor extends BaseHandler {

    private final org.apache.qpid.proton.engine.Handler delegate;

    public Processor(org.apache.qpid.proton.engine.Handler delegate, int window) {
        this.delegate = delegate != null ? delegate : this;
        add(new FlowController(window));
        add(new Handshaker());
        add(new Decoder(this.delegate));
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
