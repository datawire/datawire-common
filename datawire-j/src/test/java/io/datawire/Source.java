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
    private SimpleTag tag = new SimpleTag(1);

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
