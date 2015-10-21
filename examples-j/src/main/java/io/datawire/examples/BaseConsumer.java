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
package io.datawire.examples;

import java.io.IOException;

import javax.inject.Inject;

import org.apache.qpid.proton.reactor.Reactor;

import io.datawire.BaseDatawireHandler;

import com.github.rvesse.airline.examples.ExampleRunnable;

public class BaseConsumer extends BaseDatawireHandler   implements ExampleRunnable {

    private Reactor reactor;
    @Inject
    private ServiceConsumer consumer = new ServiceConsumer();

    public BaseConsumer() {
        super();
    }

    @Override
    public int run() {
        try {
            reactor = Reactor.Factory.create();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            return -1;
        }
        try {
            consumer.start(reactor, this);
            reactor.run();
        } finally {
            reactor.stop();
        }
        return 0;
    }

}