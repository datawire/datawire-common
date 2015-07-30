/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import java.util.Arrays;

import org.apache.qpid.proton.engine.Session;
import org.apache.qpid.proton.reactor.Reactor;

public class Receiver extends Link {

    public static class Config extends Link.Config {
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

    protected abstract static class Builder<S extends Receiver, C extends Config, B extends Builder<S, C, B>> extends Link.Builder<S, C, B> {
        public B withDrain(boolean drain) {
            config().drain = drain;
            return self();
        }
    }

    private static class ReceiverBuilder extends Builder<Receiver, Config, ReceiverBuilder> {
        private Config config = new Config();
        @Override protected Config config() { return config; }
        @Override protected ReceiverBuilder self() { return this; }
        @Override public Receiver create() {
            Config config = this.config;
            this.config = null;
            return new Receiver(config);
        }
    }

    private final Config config;

    public static Builder<?,?,?> Builder() {
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

    public Receiver(String source, String target, boolean drain, org.apache.qpid.proton.engine.Handler...handlers) {
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
            org.apache.qpid.proton.engine.Receiver rcv = ssn.receiver(String.format("%1s->%2s", config.source, config.target));
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

    @Override
    protected String getNetwork() {
        return new Address(config.source).getNetwork();
    }

}
