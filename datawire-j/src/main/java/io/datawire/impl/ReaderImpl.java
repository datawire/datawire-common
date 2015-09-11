package io.datawire.impl;

import org.apache.qpid.proton.message.Message;

import io.datawire.Entry;
import io.datawire.Reader;
import io.datawire.Store;
import io.datawire.StoreImpl;

public class ReaderImpl implements Reader {
    private final StoreImpl store;
    private final String address;
    private int serial;

    public ReaderImpl(StoreImpl store, String address) {
        this.store = store;
        this.address = address;
        this.serial = store.min();
    }

    @Override
    public String getAddress() {
        return address;
    }

    @Override
    public Entry next() {
        Entry result = null;
        for (int max = store.max(); serial < max;) {
            Entry temp = store.get(serial);
            serial += 1;
            if (!temp.isDeleted()) {
                result = temp;
                break;
            }
        }
        return result;
    }

    @Override
    public boolean more() {
        return serial < store.max();
    }

    @Override
    public void close() {
        store.close(this);
    }

    public int getSerial() {
        return serial;
    }

}
