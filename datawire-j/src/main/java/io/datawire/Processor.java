/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.reactor.FlowController;
import org.apache.qpid.proton.reactor.Handshaker;

/**
 * A handler for processing incoming messages. It aggregates a {@link FlowController}, a {@link Handshaker} and a {@link Decoder}. 
 * <p>
 * 
 * <pre>
 * {@code
 * class MyHandler extends BaseDatawireHandler {
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
 */
public class Processor extends BaseDatawireHandler {

    public Processor(Handler delegate, int window) {
        add(new FlowController(window));
        add(new Handshaker());
        add(new Decoder());
        if (delegate != null) {
            add(delegate);
        }
    }

    public Processor(Handler delegate) {
        this(delegate, 1024);
    }

    public Processor() {
        this(null);
    }
}
