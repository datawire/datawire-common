package io.datawire.impl;

import java.nio.ByteBuffer;

import io.datawire.DatawireUtils;
import io.datawire.Entry;

import org.apache.qpid.proton.message.Message;

class EntryImpl implements Entry {
    final ByteBuffer encodedMessage;
    final boolean persistent;
    final boolean deleted;
    final long timestamp = System.currentTimeMillis();
    EntryImpl(Message message, boolean persistent, boolean deleted) {
        this.encodedMessage = DatawireUtils.encode(message);
        this.persistent = persistent;
        this.deleted = deleted;
    }
    EntryImpl(ByteBuffer encodedMessage, boolean persistent, boolean deleted) {
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
