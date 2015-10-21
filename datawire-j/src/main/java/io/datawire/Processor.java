/**
 * Copyright 2015 datawire. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
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
