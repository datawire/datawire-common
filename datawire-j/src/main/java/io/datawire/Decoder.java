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

import java.nio.ByteBuffer;

import org.apache.qpid.proton.amqp.messaging.Accepted;
import org.apache.qpid.proton.amqp.messaging.Rejected;
import org.apache.qpid.proton.amqp.transport.DeliveryState;
import org.apache.qpid.proton.amqp.transport.SenderSettleMode;
import org.apache.qpid.proton.engine.Delivery;
import org.apache.qpid.proton.engine.ExtendableAccessor;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.Link;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Receiver;
import org.apache.qpid.proton.engine.Sender;
import org.apache.qpid.proton.message.Message;

/**
 * Handler for decoding deliveries into messages.
 * <p>
 * The Decoder fires the {@link DatawireHandler#onEncodedMessage(DatawireEvent)}
 * and {@link DatawireHandler#onMessage(DatawireEvent)} synchronously on the
 * {@link Event#getRootHandler()} and depending on success or failure (exception
 * being thrown) either accepts ({@link Delivery#disposition(DeliveryState)})
 * or rejects the delivery and settles it ({@link Delivery#settle()})
 * <p>
 * <b>Usage</b>: Implement a {@link DatawireHandler} preferably by extending the
 * {@link BaseDatawireHandler}, implement the
 * {@link DatawireHandler#onMessage(DatawireEvent)} and add a Decoder as a child
 * handler or the other way around.
 * <p>
 * 
 */
public class Decoder extends BaseDatawireHandler {
    private static final ExtendableAccessor<Event, Boolean> IS_DONE = new ExtendableAccessor<>(Boolean.class);
    private static final Accepted ACCEPTED = Accepted.getInstance();
    private static final Rejected REJECTED = new Rejected();

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
     * An instance of decoder that will invoke {@link DatawireHandler#onEncodedMessage(DatawireEvent)}
     * {@link DatawireHandler#onMessage(DatawireEvent)} on the
     * {@link Event#getRootHandler()}
     * 
     * @param children
     *            the optional child handlers to install.
     */
    /**
     * @param children
     */
    public Decoder(Handler... children) {
        for (Handler child : children) {
            add(child);
        }
    }

    public static boolean isDone(Event e) {
        return Boolean.TRUE.equals(IS_DONE.get(e));
    }

    @Override
    public void onDelivery(Event e) {
        Delivery dlv = e.getDelivery();
        if (isDone(e)) {
            return; 
        }
        if (!recv(message, dlv)) { // TODO: move to Message
            return;
        }
        try {
            IS_DONE.set(e, Boolean.TRUE);
            Handler root = e.getRootHandler();
            DatawireEvent.MESSAGE_ACCESSOR.set(e, message);
            e.redispatch(DatawireEvent.Type.ENCODED_MESSAGE, root);
            e.redispatch(DatawireEvent.Type.MESSAGE, root);
            e.delegate();
            dlv.disposition(ACCEPTED);
        } catch (Throwable ex) {
            dlv.disposition(REJECTED); // TODO: setErrorCondition?
            throw ex; // XXX: Why does python Decoder not re-throw???
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
        int received = recv.recv(buffer, 0, dlv.pending());
        recv.advance();
        if (recv.getRemoteSenderSettleMode() == SenderSettleMode.SETTLED) {
            dlv.settle();
        }
        message2.decode(buffer, 0, received);
        ByteBuffer encoded = ByteBuffer.wrap(buffer, received, buffer.length
                - received);
        encoded.flip();
        DatawireEvent.ENCODED_MESSAGE_ACCESSOR.set(dlv, encoded);
        return true;
    }
}
