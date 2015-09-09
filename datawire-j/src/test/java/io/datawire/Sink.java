package io.datawire;

import java.util.ArrayList;
import java.util.Map;

import org.apache.qpid.proton.amqp.messaging.AmqpSequence;
import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.amqp.messaging.Section;
import org.apache.qpid.proton.message.Message;

public class Sink extends Processor {
    private ArrayList<Section> messages = new ArrayList<Section>();

    @Override
    public void onMessage(DatawireEvent e) {
        Message msg = e.getMessage();
        messages.add(msg.getBody());
    }

    public ArrayList<String> getMessages() {
        ArrayList<String> ret = new ArrayList<String>(messages.size());
        for (Section body : messages) {
            ret.add(DatawireUtils.stringify(body));
        }
        return ret;
    }
    
    public ArrayList<Map<?,?>> getMessagesDicts() {
        ArrayList<Map<?,?>> ret = new ArrayList<Map<?,?>>(messages.size());
        for (Section body : messages) {
            if (body instanceof AmqpValue) {
                Object value = ((AmqpValue)body).getValue();
                if (value instanceof Map<?,?>) {
                    ret.add((Map<?,?>)value);
                } else {
                    ret.add(null);
                }
            } else {
                ret.add(null);
            }
        }
        return ret;
    }
}