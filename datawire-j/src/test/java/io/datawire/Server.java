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

import java.io.IOException;

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.reactor.Acceptor;

public class Server extends BaseTestHandler {
    public static final int PORT = 5678;
    private String host = "localhost";
    private Handler delegate;
    private int opened = 0;
    private int closed = 0;
    private int maxConnections = Integer.MAX_VALUE;
    private Acceptor acceptor;

    @Override
    public void onOpened(Event e) {
        opened += 1;
    }

    @Override
    public void onClosed(Event e) {
        closed += 1;
        if (closed >= maxConnections) {
            close();
        }
    }

    @Override
    public void onReactorInit(Event e) {
        try {
            acceptor = e.getReactor().acceptor(host, PORT, new Closer(delegate, this));
        } catch (IOException e1) {
            throw new RuntimeException("Cannot create acceptor", e1);
        }
    }

    @Override
    public void onReactorFinal(Event e) {
        close();
    }

    private void close() {
        if (acceptor != null) {
            Acceptor acceptor = this.acceptor;
            this.acceptor = null;
            acceptor.close();
        }
    }
 
    public Server(Handler delegate) {
        this.delegate = delegate;
    }

    public void setMaxConnections(int i) {
        maxConnections = i;
    }

    public String address() {
        return String.format("//%s:%s", host, PORT);
    }

    public String address(Object extra) {
        return String.format("//%s:%s/%s", host, PORT, extra.toString());
    }
}
