package io.datawire;

import io.datawire.impl.ReaderImpl;

public interface StoreImpl extends Store {

    public int min();

    public int max();

    public Entry get(int serial);

    public void close(ReaderImpl reader);
}
