package io.datawire;

import java.nio.ByteBuffer;

public interface Entry {

    ByteBuffer getEncodedMessage();

    boolean isPersistent();

    boolean isDeleted();

    long getTimestamp();

}