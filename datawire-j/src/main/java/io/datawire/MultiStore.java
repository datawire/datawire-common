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

import org.apache.qpid.proton.message.Message;

/**
 * TBD: drop this, it's just a store, except for ...
 * 
 * Note: MultiStore preserves only partial ordering, per message address as specified in {@link Store#put(Message, String)}
 */
public interface MultiStore extends Store {
    public static class Factory {
        public static MultiStore create() { return null; }
    }
}
