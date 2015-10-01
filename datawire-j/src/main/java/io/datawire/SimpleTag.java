package io.datawire;

import java.nio.charset.Charset;

import org.apache.qpid.proton.engine.Delivery;

/**
 * A generator for {@link Delivery} tags. The tag is UTF8 encoded string
 * representation of an integer counter
 *
 */
public class SimpleTag implements Tag {
    private static final Charset UTF8 = Charset.forName("UTF-8");
    private int tag;

    /**
     * @param tag initial value to generate
     */
    public SimpleTag(int tag) {
        this.tag = tag;
    }

    @Override
    public byte[] deliveryTag() {
        return String.valueOf(tag++).getBytes(UTF8);
    }
}