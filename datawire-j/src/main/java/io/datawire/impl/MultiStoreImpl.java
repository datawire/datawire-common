package io.datawire.impl;

import java.nio.ByteBuffer;
import java.util.HashMap;

import org.apache.qpid.proton.message.Message;

import io.datawire.BaseDatawireHandler;
import io.datawire.MultiStore;
import io.datawire.Reader;
import io.datawire.Store;
import io.datawire.StoreImpl;

public class MultiStoreImpl extends BaseDatawireHandler implements MultiStore {
    
    private HashMap<String, StoreImpl> stores = new HashMap<>();
    private int size = 0;
    private long last_idle = 0;
    private long max_idle = 0;

    @Override
    public void put(Message msg, String address) {
        StoreImpl store = lookup(address);
        if (store == null)
            return; // XXX: caller will have a hard time figuring out nothing happened
        store.put(msg, address);
        size += 1;
    }

    @Override
    public void put(ByteBuffer encodedMessage, String address) {
        StoreImpl store = lookup(address);
        if (store == null)
            return; // XXX: caller will have a hard time figuring out nothing happened
        store.put(encodedMessage, address);
        size += 1;
    }

    private StoreImpl lookup(String address) {
        StoreImpl store = stores.get(address);
        if (store == null) {
            store = resolve(address);
            if (store == null) {
                return null;
            }
            stores.put(address, store);
        }
        return store;
    }

    private StoreImpl resolve(String address) {
        return new TransientStore();
    }

    @Override
    public Reader reader(String address) {
        StoreImpl store = lookup(address);
        if (store == null)
            return null;
        return store.reader(address);
    }

    @Override
    public int gc() {
        int reclaimed = 0;
        for (String k : stores.keySet().toArray(new String[stores.size()])) {
            StoreImpl s = stores.get(k);
            reclaimed += s.gc();
            last_idle = s.getLastIdle();
            max_idle = Math.max(max_idle, s.getMaxIdle());
            if (s.isEmpty()) {
                stores.remove(k);
            }
        }
        size -= reclaimed;
        return reclaimed;
    }

    @Override
    public void flush() {
        for (Store s : stores.values()) {
            s.flush();
        }
    }

    @Override
    public long getLastIdle() {
        return last_idle;
    }

    @Override
    public long getMaxIdle() {
        return max_idle;
    }

    @Override
    public int size() {
        return size;
    }

    @Override
    public boolean isEmpty() {
        return stores.size() == 0;
    }

}