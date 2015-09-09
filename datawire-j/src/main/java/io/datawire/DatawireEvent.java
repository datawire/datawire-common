/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import org.apache.qpid.proton.engine.Delivery;
import org.apache.qpid.proton.engine.EventType;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.Record;
import org.apache.qpid.proton.message.Message;

/**
 * Events generated by the datawire library
 * @author bozzo
 *
 */
public interface DatawireEvent extends org.apache.qpid.proton.engine.Event {

    /**
     * Event types generated by the datawire library
     * @author bozzo
     *
     */
    public enum Type implements EventType {
        /**
         * An event holding a {@link Message} that was decoded from a {@link Delivery}. See {@link Decoder}.
         */
        MESSAGE,
        /**
         * An event signaling the next sampling interval for the link. See {@link Sampler}.
         */
        SAMPLE,
        /**
         * An event 
         */
        DRAINED,
        /**
         * A guard value returned by {@link Event#getDatawireType()} when this method is invoked on a non-datawire {@link org.apache.qpid.proton.engine.Event} instance.
         * This value is not valid for {@link Event#redispatch(EventType, Handler)}, see {@link EventType#isValid()}
         */
        NOT_A_DATAWIRE_TYPE {
            /**
             * {@inheritDoc}
             */
            @Override
            public boolean isValid() {
                return false;
            }
        };

        /**
         * {@inheritDoc}
         */
        @Override
        public void dispatch(org.apache.qpid.proton.engine.Event e, Handler h) {
            io.datawire.impl.DatawireEventTypeImpl.dispatch(this, e, h);
        }

        /**
         * {@inheritDoc}
         */
        @Override
        public boolean isValid() {
            return true;
        }
    }

    public static final Record.Accessor<Message> MESSAGE_ACCESSOR = new Record.Accessor<Message>() {
            @Override public Message get(Record r) { return r.get(this, Message.class); }
            @Override public void set(Record r, Message value) { r.set(this, Message.class, value); }
        };

    /**
     * @return {@link Type} of datawire event or {@link Type#NOT_A_DATAWIRE_TYPE} when invoked on non-datawire event.
     * <p>
     * Useful for handling datawire events with a {@code switch(event.getDatawireType())} inside a {@link Handler#onUnhandled(org.apache.qpid.proton.engine.Event)}
     */
    Type getDatawireType();

    /**
     * @return {@link Message} for {@link Type#MESSAGE} events
     */
    Message getMessage();
}
