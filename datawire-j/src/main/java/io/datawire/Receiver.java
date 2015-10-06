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

import io.datawire.Sender.SenderBuilder;

import java.util.Arrays;

import org.apache.qpid.proton.engine.Session;
import org.apache.qpid.proton.reactor.Reactor;

/**
 * Handler for managing a {@link org.apache.qpid.proton.engine.Receiver} on an
 * outgoing connection
 */
public class Receiver extends Link {

    /**
     * Configuration for a {@link Receiver}.
     * <p>
     * A receiver must have a valid {@link Link.Config#source}
     * 
     */
    public static class Config extends Link.Config {
        /**
         * initial value for
         * {@link org.apache.qpid.proton.engine.Receiver#setDrain(boolean)

         */
        public boolean drain = false;

        @Override
        public int hashCode() {
            final int prime = 31;
            int result = super.hashCode();
            result = prime * result + (drain ? 1231 : 1237);
            return result;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj)
                return true;
            if (!super.equals(obj))
                return false;
            if (!(obj instanceof Config))
                return false;
            Config other = (Config) obj;
            if (drain != other.drain)
                return false;
            return true;
        }
    }

    /**
     * Reusable part of builder for the {@link Receiver}.
     *
     * @param <S>
     * @param <C>
     * @param <B>
     */
    protected abstract static class Builder<S extends Receiver, C extends Config, B extends Builder<S, C, B>>
            extends Link.Builder<S, C, B> {
        /**
         * @param drain
         *            set the {@link Config#drain}
         * @return The builder
         */
        public B withDrain(boolean drain) {
            config().drain = drain;
            return self();
        }
    }

    /**
     * Builder for {@link Receiver}
     *
     */
    private static class ReceiverBuilder extends
            Builder<Receiver, Config, ReceiverBuilder> {
        private Config config = new Config();

        @Override
        protected Config config() {
            return config;
        }

        @Override
        protected ReceiverBuilder self() {
            return this;
        }

        /**
         * Create the {@link Receiver} as configured. The Builder is not usable
         * after this call.
         */
        @Override
        public Receiver create() {
            Config config = this.config;
            this.config = null;
            return new Receiver(config);
        }
    }

    private final Config config;

    /**
     * @return a new {@link ReceiverBuilder}
     */
    public static Builder<?, ?, ?> Builder() {
        return new ReceiverBuilder();
    }

    private static Config validate(Config config) {
        if (config.source == null)
            throw new IllegalArgumentException("source is required");
        return config;
    }

    private Receiver(Config config) {
        super(validate(config));
        this.config = config;
    }

    /**
     * Reference constructor
     * 
     * @param source
     *            Receiver source address, mandatory
     * @param target
     *            Receiver target address, optional
     * @param drain
     *            Drain flag
     * @param handlers
     *            Child handlers for the link
     */
    public Receiver(String source, String target, boolean drain,
            org.apache.qpid.proton.engine.Handler... handlers) {
        super(handlers);
        config = new Config();
        config.source = source;
        config.target = target;
        config.drain = drain;
        config.handlers.addAll(Arrays.asList(handlers));
        validate(config);
    }

    private final LinkCreator link = new LinkCreator() {

        @Override
        public org.apache.qpid.proton.engine.Link create(Reactor reactor) {
            Session ssn = _session(reactor);
            org.apache.qpid.proton.engine.Receiver rcv = ssn.receiver(String
                    .format("%1s->%2s", config.source, config.target));
            rcv.setDrain(config.drain);
            setLinkSource(rcv, config.source);
            setLinkTarget(rcv, config.target);
            return rcv;
        }

    };

    @Override
    protected LinkCreator getLinkCreator() {
        return link;
    }

    /**
     * Source network address
     */
    @Override
    protected String getNetwork() {
        return new Address(config.source).getNetwork();
    }

}
