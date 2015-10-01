package io.datawire;

import java.nio.ByteBuffer;

import org.apache.qpid.proton.message.Message;

/**
 * An ordered store for AMQP messages
 * 
 */
public interface Store {
    public static class Factory {
        public static Store create() {
            return new io.datawire.impl.TransientStore();
        }
    }

    /**
     * Encode the message and enqueue it
     * 
     * @param msg
     *            The message
     * @param address
     *            The address under which to track this message
     *            <p>
     *            XXX: should this not be this be message.address???
     */
    public void put(Message msg, String address);

    /**
     * Enqueue the encoded message
     * 
     * @param buffer
     *            The encoded message
     * @param address
     *            The address under which to track this message
     */
    public void put(ByteBuffer buffer, String address);

    /**
     * A mechanism to consume messages from the Store
     * 
     * @param address
     *            The address filter ???
     * @return A reader object
     */
    public Reader reader(String address);

    /**
     * Checkpoint the store to the persistent medium (TODO)
     */
    public void flush();

    /**
     * Garbage collect the entries that are already consumed by all active
     * readers. A {@link Store} subclass can keep old entries around
     * 
     * @return the number of entries actually removed
     */
    public int gc();

    /**
     * @return age of the oldest entry in the store
     */
    public long getLastIdle();

    /**
     * @return biggest {@link #getLastIdle()} observed in the lifetime of the
     *         {@link Store}
     */
    public long getMaxIdle();

    /**
     * @return Number of entries in the {@link Store}
     */
    public int size();

    /**
     * @return True when there are no entries in the {@link Store}
     */
    public boolean isEmpty();

}
