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

import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Sender;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.Handshaker;

public class Source extends BaseDatawireHandler {
    private Template template;
    private int count = 0;
    private int limit = Integer.MAX_VALUE;
    private int window = 1024;
    private Message message = Message.Factory.create();
    private Tag tag = new SimpleTag(1);

    public Source(Template template) {
        this.template = template;
        add(new Handshaker());
    }

    @Override
    public void onLinkFlow(Event e) {
        org.apache.qpid.proton.engine.Link link = e.getLink();
        if (link instanceof Sender) {
            Sender sender = (Sender)link;
            pump(sender);
        }
    }

    private void pump(Sender sender) {
        while (count < limit && sender.getCredit() > 0 && sender.getQueued() < window) {
            message.setBody(new AmqpValue(template.render(count)));
            DatawireUtils.send(sender, tag, message);
            count += 1;
        }
    }

    public void setLimit(int limit) {
        this.limit = limit;
    }
}
