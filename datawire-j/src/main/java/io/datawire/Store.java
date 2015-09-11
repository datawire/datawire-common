package io.datawire;
import java.nio.ByteBuffer;

import org.apache.qpid.proton.message.Message;


public interface Store extends DatawireHandler {
    public static class Factory {
        public static Store create() {
            return new io.datawire.impl.TransientStore();
        }
    }

    public void put(Message msg, String address);
    public void put(ByteBuffer buffer, String address);
    public Reader reader(String address);

    public void flush();
    public int gc();

    public long getLastIdle();
    public long getMaxIdle();

    public int size();
    public boolean isEmpty();

}
