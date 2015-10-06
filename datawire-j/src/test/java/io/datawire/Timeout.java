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
