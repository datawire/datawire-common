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

import java.nio.ByteBuffer;

/**
 * A queued encoded message in the {@link Store} accessible by {@link Store#reader(String)}
 */
public interface Entry {

    /**
     * Encoded message
     * @return The ByteBuffer containing the message
     */
    ByteBuffer getEncodedMessage();

    /**
     * Persistent flag
     * @return whether the entry is persistent
     */
    boolean isPersistent();

    /**
     * Deleted flag
     * @return whether the entry is deleted (TBD: what are deleted entries)
     */
    boolean isDeleted();

    /**
     * Timestamp when Entry was added
     * @return Timestamp the entry was added
     */
    long getTimestamp();
}