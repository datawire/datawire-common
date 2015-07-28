/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import java.util.Arrays;

import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.Session;
import org.apache.qpid.proton.reactor.Reactor;

public class Receiver extends Link {
    
    private static class Config extends Link.Config {
        public Link.Config link;
        public String source;
        public String target;
        public boolean drain = false; //XXX: TODO constructor explosion, or think about builder pattern
    }
    
    public static class Builder {
        Config config = new Config();
        public Builder setSource(String source) {
            config.source = source;
            return this;
        }
        public Builder setTarget(String target) {
            config.target = target;
            return this;
        }
        public Builder setDrain(boolean drain) {
            config.drain = drain;
            return this;
        }
        public Builder addHandler(Handler handler) {
            config.handlers.add(handler);
            return this;
        }
        public Receiver create() {
            Config config = this.config;
            this.config = null;
            return new Receiver(config);
        }
    }
    
    private final Config config;
    
    public static Builder Builder() {
        return new Builder();
    }
    
    private Receiver(Config config) {
        super(config);
        this.config = config;
    }
    
    public Receiver(String source, String target, boolean drain, org.apache.qpid.proton.engine.Handler...handlers) {
        super(handlers);
        config = new Config();
        config.source = source;
        config.target = target;
        config.drain = drain;
        config.handlers.addAll(Arrays.asList(handlers));
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
