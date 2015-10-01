package io.datawire;


/**
 * A {@link Store} reader that reads messages in the order they were queued
 *
 */
public interface Reader {
    /**
     * 
     * @return Address for which the messages are read
     */
    String getAddress();
    /**
     * @return next unread {@link Entry} or <code>null</code> if not {@link #more()}
     */
    Entry next();
    /**
     * 
     * @return True if there are Entries to be read
     */
    boolean more();
    /**
     * Dissociate the {@link Reader} from the {@link Store}
     */
    void close();
}
