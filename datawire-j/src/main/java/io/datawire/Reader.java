package io.datawire;


public interface Reader {
    String getAddress();
    Entry next();
    boolean more();
    void close();
}
