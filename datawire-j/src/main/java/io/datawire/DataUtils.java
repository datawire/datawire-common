package io.datawire;

import java.nio.BufferOverflowException;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.util.Map;

import org.apache.qpid.proton.amqp.Binary;
import org.apache.qpid.proton.amqp.Symbol;
import org.apache.qpid.proton.message.Message;

public class DataUtils {

    static final Charset UTF8_CHARSET = Charset.forName("UTF-8");

    static String getInfo(Map info, Symbol key) {
        if (info == null || key == null)
            return null;
        return stringify(info.get(key));
    }

    static String stringify(Object value) {
        if (value instanceof String) {
            return (String) value;
        } else if (value instanceof Binary) {
            return new String(((Binary)value).getArray(), UTF8_CHARSET);
        }
        return null;
    }

    static ByteBuffer encode(Message msg) {
        int size = 1000;
        while(true) {
            try {
                byte[] bytes = new byte[size];
                int length = msg.encode(bytes, 0, size);
                return ByteBuffer.wrap(bytes, length, size-length);
            } catch (BufferOverflowException ex) {
                size *= 2;
                continue; 
            }
        }
    }

}
