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

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Handler;

public class Closer extends BaseDatawireHandler {
    public Closer(Handler delegate, TestHandler closer) {
        add(delegate);
        add(closer);
    }
    @Override
    public void onConnectionBound(Event e) {
        e.delegate();
        e.redispatch(TestEvent.Type.OPENED, this);
    }
    @Override
    public void onConnectionUnbound(Event e) {
        e.delegate();
        e.redispatch(TestEvent.Type.CLOSED, this);
    }
}
