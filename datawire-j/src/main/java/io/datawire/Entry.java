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