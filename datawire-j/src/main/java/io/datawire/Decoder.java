/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
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

/**
 * Handler for decoding deliveries into messages.
 * <p>
 * <b>Usage</b>: Implement a {@link Handler} preferably by extending the
 * {@link BaseHandler}, implement the {@link Handler#onMessage(DatawireEvent)} and then
 * either
 * <ul>
 * <li>pass it as {@code delegate} to the
 * {@link Decoder#Decoder(org.apache.qpid.proton.engine.Handler)} constructor,
 * or</li>
 * <li>add your handler with
 * {@link Decoder#add(org.apache.qpid.proton.engine.Handler)} to an instance of
 * {@link #Decoder()}</li>
 * </ul>
 *
 * The Decoder fires the {@link Handler#onMessage(DatawireEvent)} synchronously and
 * depending on success or failure (exception being thrown) either accepts (
 * {@link Delivery#disposition(org.apache.qpid.proton.amqp.transport.DeliveryState)}
 * ) or rejects the delivery and settles it ({@link Delivery#settle()})
 * <p>
 * TODO: for simple scenarios use the ServiceBase class
 * 
 * @author bozzo
 *
 */
public class Decoder extends BaseHandler {
    private static final Accepted ACCEPTED = Accepted.getInstance();
    private static final Rejected REJECTED = new Rejected();

    private final org.apache.qpid.proton.engine.Handler delegate;

    // FIXME: one instance of Message is dangerous, user of the API can easily
    // use the same Decoder instance with two reactors! It would be better if
    // message was associated with datawire EventImpl and kept as part of the
    // pool
    // FIXME: Event.copy does not copy deep enough. A handler that would build
    // something akin Sampler on top of Decoder to refer to a message will get
    // the message changed from under it.
    private Message message = Message.Factory.create();
    private byte[] buffer = new byte[10000];

    /**
     * An instance of decoder that will use itself as the delegate, see
     * {@link #Decoder(org.apache.qpid.proton.engine.Handler)}
     * <p>
     * Use this constructor when deriving or adding your handler via
     * {@link Decoder#add(org.apache.qpid.proton.engine.Handler)}
     */
    public Decoder() {
        this(null);
    }

    /**
     * An instance of decoder that will invoke {@link Handler#onMessage(DatawireEvent)}
     * on the supplied delegate
     * <p>
     * XXX: is it ever a good idea to use this approach? Deprecate?
     * 
     * @param delegate the handler to invoke with decoded messages. Can be {@literal null}.
     */
    public Decoder(org.apache.qpid.proton.engine.Handler delegate) {
        this.delegate = delegate != null ? delegate : this;
    }

    @Override
    public void onDelivery(org.apache.qpid.proton.engine.Event e) {
        Delivery dlv = e.getDelivery();
        if (!recv(message, dlv)) { // TODO: move to Message
            return;
        }
        try {
            e.attachments().set(EventImpl.MESSAGE, Message.class, message);
            e.redispatch(DatawireEvent.Type.MESSAGE, delegate);
            dlv.disposition(ACCEPTED);
        } catch (Throwable ex) {
            dlv.disposition(REJECTED); // TODO: setErrorCondition?
            throw ex; // XXX: Why does python Decoder not re-throw???
        } finally {
            dlv.settle();
        }
    }

    @Override
    public void onMessage(DatawireEvent e) {
        // XXX: is this really really necessary?
        // When this instance is used as the delegate it should not forward this
        // event to the onUnhandled.
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
