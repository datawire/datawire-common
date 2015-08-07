package io.datawire;

public class SimpleTag {
    public int tag;

    public SimpleTag(int tag) {
        this.tag = tag;
    }

    protected byte[] deliveryTag() {
        return String.valueOf(tag++).getBytes();
    }
}