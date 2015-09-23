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
