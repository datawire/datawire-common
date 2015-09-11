package io.datawire;

public class SimpleTag implements Tag {
    public int tag;

    public SimpleTag(int tag) {
        this.tag = tag;
    }

    @Override
    public byte[] deliveryTag() {
        return String.valueOf(tag++).getBytes();
    }
}