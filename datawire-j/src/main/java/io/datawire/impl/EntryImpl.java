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
package io.datawire.impl;

import java.nio.ByteBuffer;

import io.datawire.DatawireUtils;
import io.datawire.Entry;

import org.apache.qpid.proton.message.Message;

public class EntryImpl implements Entry {
    private final ByteBuffer encodedMessage;
    private final boolean persistent;
    private final boolean deleted;
    private final long timestamp = System.currentTimeMillis();
    public EntryImpl(Message message, boolean persistent, boolean deleted) {
        this.encodedMessage = DatawireUtils.encode(message);
        this.persistent = persistent;
        this.deleted = deleted;
    }
    public EntryImpl(ByteBuffer encodedMessage, boolean persistent, boolean deleted) {
        this.encodedMessage = encodedMessage;
        this.persistent = persistent;
        this.deleted = deleted;
    }
    @Override
    public ByteBuffer getEncodedMessage() {
        return encodedMessage;
    }
    @Override
    public boolean isPersistent() {
        return persistent;
    }
    @Override
    public boolean isDeleted() {
        return deleted;
    }
    @Override
    public long getTimestamp() {
        return timestamp;
    }
}
