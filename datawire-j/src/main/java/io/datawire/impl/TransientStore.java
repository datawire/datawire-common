package io.datawire.impl;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.logging.Logger;

import org.apache.qpid.proton.message.Message;

import io.datawire.BaseDatawireHandler;
import io.datawire.Entry;
import io.datawire.Reader;
import io.datawire.StoreImpl;
import io.datawire.Stream;

public class TransientStore extends BaseDatawireHandler implements StoreImpl {
    private static final Logger log = Logger.getLogger(TransientStore.class.getName());
    private ArrayList<EntryImpl> entries = new ArrayList<>();
    private int serial = 0;
    private ArrayList<ReaderImpl> readers = new ArrayList<>();
    private int lastflush = 0;
    private long max_idle = 0;
    private long last_idle = 0;
    private int lastgc = 0;

    public TransientStore() {}
    public TransientStore(String name){
        if (name != null) {
            log.warning("This store is transient, TODO persistence to " + name);
        }
    }

    @Override
    public void put(Message msg, String address) {
        entries.add(new EntryImpl(msg, true, false));
    }

    @Override
    public void put(ByteBuffer buffer, String address) {
        entries.add(new EntryImpl(buffer, true, false));
    }

    @Override
    public Reader reader(String address) {
        ReaderImpl reader = new ReaderImpl(this, address);
        readers.add(reader);
        return reader;
    }

    @Override
    public int max() {
        return serial + entries.size();
    }

    @Override
    public int min() {
        return serial;
    }

    @Override
    public Entry get(int serial) {
        return entries.get(serial - this.serial);
    }

    @Override
    public void flush() {
        lastflush = max();
    }

    @Override
    public int gc() {
        int serial = max();
        for (ReaderImpl r : readers) {
            serial = Math.min(serial, r.getSerial());
        }
        long now = System.currentTimeMillis();
        if (entries.size() > 0) {
            max_idle  = Math.max(now - entries.get(0).getTimestamp(), max_idle);
        }
        if (serial == lastgc )
            return 0;
        int reclaimed = 0;
        if (this.serial < serial) {
            int delta = serial - this.serial;
            List<EntryImpl> head = entries.subList(0, delta);
            List<EntryImpl> tail = compact(head);
            reclaimed = delta - tail.size();
            last_idle  = now - entries.get(reclaimed - 1).getTimestamp();
            max_idle = Math.max(last_idle, max_idle);
            head.clear();
            head.addAll(tail);
            this.serial += reclaimed;
        }
        lastgc = serial;
        // TODO Auto-generated method stub
        return reclaimed;
    }

    protected List<EntryImpl> compact(List<EntryImpl> head) {
        return Collections.emptyList();
    }

    @Override
    public void close(ReaderImpl reader) {
        readers.remove(reader);
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
    public boolean isEmpty() {
        return entries.size() == 0 && readers.size() == 0;
    }

    @Override
    public int size() {
        return entries.size();
    }
}
