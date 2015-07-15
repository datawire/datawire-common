package io.datawire;

import io.datawire.impl.EventImpl;

import org.apache.qpid.proton.amqp.messaging.Accepted;
import org.apache.qpid.proton.amqp.messaging.Rejected;
import org.apache.qpid.proton.amqp.transport.SenderSettleMode;
import org.apache.qpid.proton.engine.Delivery;
import org.apache.qpid.proton.engine.Link;
import org.apache.qpid.proton.engine.Receiver;
import org.apache.qpid.proton.engine.Sender;
import org.apache.qpid.proton.message.Message;

public class Decoder extends BaseHandler {
    private static final Accepted ACCEPTED = Accepted.getInstance();
    private static final Rejected REJECTED = new Rejected();

    private Handler delegate;
    
    // FIXME: one instance of Message is dangerous, user of the API can easily use the same Decoder
    // instance with two reactors! It would be better if message was associated
    // with datawire EventImpl and kept as part of the pool
    private Message message = Message.Factory.create();
    private byte[] buffer = new byte[10000];

    public Decoder() {
        this.delegate = this;
    }

    public Decoder(Handler delegate) {
        this.delegate = delegate;
    }

    @Override
    public void onDelivery(org.apache.qpid.proton.engine.Event e) {
        Delivery dlv = e.getDelivery();
        if (!recv(message, dlv)) {        // TODO: move to Message
            return;
        }               
        try {
            e.attachments().set(EventImpl.MESSAGE, Message.class, message);
            Event.Type.MESSAGE.dispatch(e, delegate);
            dlv.disposition(ACCEPTED);
        } catch (Throwable ex) {
            dlv.disposition(REJECTED);     // TODO: setErrorCondition?
            throw ex;                      // TODO: Why does python Decoder not re-throw???
        } finally {
            dlv.settle();
        }
    }

    private boolean recv(Message message2, Delivery dlv) {
        Link link = dlv.getLink();
        if (link instanceof Sender) {
            return false;
        }
        if (dlv.isPartial()) {
            return false;
        }
        if (dlv.pending() > buffer.length) {
            buffer = new byte[dlv.pending()];
        }
        Receiver recv = (Receiver) link;
        int encoded = recv.recv(buffer, 0, dlv.pending());
        recv.advance();
        if (recv.getRemoteSenderSettleMode() == SenderSettleMode.SETTLED) {
            dlv.settle();
        }
        message2.decode(buffer, 0, encoded);
        return true;
    }
}
