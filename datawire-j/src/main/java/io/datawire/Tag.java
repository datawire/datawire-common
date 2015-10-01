package io.datawire;

/**
 * A delivery tag generator
 *
 */
public interface Tag {

    /**
     * @return a new delivery tag
     */
    byte[] deliveryTag();

}