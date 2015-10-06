/**
 * Copyright 2015 datawire. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
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