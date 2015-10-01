package io.datawire;

import java.nio.BufferOverflowException;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.util.Map;

import org.apache.qpid.proton.amqp.Binary;
import org.apache.qpid.proton.amqp.Symbol;
import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.engine.Delivery;
import org.apache.qpid.proton.engine.Extendable;
import org.apache.qpid.proton.engine.ExtendableAccessor;
import org.apache.qpid.proton.engine.Record;
import org.apache.qpid.proton.engine.Sender;
import org.apache.qpid.proton.engine.Link;
import org.apache.qpid.proton.message.Message;

/**
 * Helper methods for working with proton engine
 *
 */
public class DatawireUtils {

    public static final ExtendableAccessor<Sender, Tag> SENDER_TAG = new ExtendableAccessor<Sender, Tag>(Tag.class);

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
        } else if (value instanceof AmqpValue) {
            return stringify(((AmqpValue)value).getValue());
        }
        return null;
    }

    public static ByteBuffer encode(Message msg) {
        int size = 1000;
        while(true) {
            try {
                byte[] bytes = new byte[size];
                int length = msg.encode(bytes, 0, size);
                ByteBuffer ret = ByteBuffer.wrap(bytes, length, size-length);
                ret.flip();
                return ret;
            } catch (BufferOverflowException ex) {
                size *= 2;
                continue; 
            }
        }
    }

    public static void send(final org.apache.qpid.proton.engine.Sender sender,
            Tag tag, ByteBuffer bytes) {
        Delivery dlv = sender.delivery(tag.deliveryTag());
        sender.send(bytes.array(), bytes.position(), bytes.limit());
        dlv.settle();
    }

    public static void send(final org.apache.qpid.proton.engine.Sender sender,
            ByteBuffer bytes) {
        send(sender, senderTag(sender), bytes);
    }

    public static Tag senderTag(Sender sender) {
        Tag tag = SENDER_TAG.get(sender);
        if (tag == null) {
            tag = new SimpleTag(0);
            SENDER_TAG.set(sender, tag);
        }
        return tag;
    }

    public static void send(Sender sender, Tag tag, Message message) {
        send(sender, tag, encode(message));
    }
    
    public static void send(Link link, Tag tag, Message message) {
        send((Sender)link, tag, message);
    }

}
