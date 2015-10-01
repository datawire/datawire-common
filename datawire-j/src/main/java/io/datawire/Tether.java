/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.qpid.proton.amqp.messaging.AmqpSequence;
import org.apache.qpid.proton.amqp.messaging.ApplicationProperties;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.Reactor;

/**
 * Publish service physical address to directory
 */
public class Tether extends BaseDatawireHandler {

    public static class Config {
        public String directory;
        public String address;
        public String redirect_target;
        public String host;
        public String port;
        public String policy;
        public String agent_type;

        @Override
        public int hashCode() {
            final int prime = 31;
            int result = 1;
            result = prime * result
                    + ((address == null) ? 0 : address.hashCode());
            result = prime * result
                    + ((agent_type == null) ? 0 : agent_type.hashCode());
            result = prime * result
                    + ((directory == null) ? 0 : directory.hashCode());
            result = prime * result + ((host == null) ? 0 : host.hashCode());
            result = prime * result
                    + ((policy == null) ? 0 : policy.hashCode());
            result = prime * result + ((port == null) ? 0 : port.hashCode());
            result = prime
                    * result
                    + ((redirect_target == null) ? 0 : redirect_target
                            .hashCode());
            return result;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj)
                return true;
            if (obj == null)
                return false;
            if (!(obj instanceof Config))
                return false;
            Config other = (Config) obj;
            if (address == null) {
                if (other.address != null)
                    return false;
            } else if (!address.equals(other.address))
                return false;
            if (agent_type == null) {
                if (other.agent_type != null)
                    return false;
            } else if (!agent_type.equals(other.agent_type))
                return false;
            if (directory == null) {
                if (other.directory != null)
                    return false;
            } else if (!directory.equals(other.directory))
                return false;
            if (host == null) {
                if (other.host != null)
                    return false;
            } else if (!host.equals(other.host))
                return false;
            if (policy == null) {
                if (other.policy != null)
                    return false;
            } else if (!policy.equals(other.policy))
                return false;
            if (port == null) {
                if (other.port != null)
                    return false;
            } else if (!port.equals(other.port))
                return false;
            if (redirect_target == null) {
                if (other.redirect_target != null)
                    return false;
            } else if (!redirect_target.equals(other.redirect_target))
                return false;
            return true;
        }
    }

    public abstract static class Builder<S extends Tether, C extends Config, B extends Builder<S, C, B>> extends ExtensibleBuilder<S, C, B> {
        /**
         * @param directory directory address
         * @return self
         */
        public B withDirectory(String directory) {
            config().directory = directory;
            return self();
        }
        /**
         * @param address logical address
         * @return self
         */
        public B withAddress(String address) {
            config().address = address;
            return self();
        }
        /**
         * @param redirect_target physical address
         * @return self
         */
        public B withRedirectTarget(String redirect_target) {
            config().redirect_target = redirect_target;
            return self();
        }
        /**
         * 
         * @param host 
         * @return
         */
        public B withHost(String host) {
            config().host = host;
            return self();
        }
        public B withPort(String port) {
            config().port = port;
            return self();
        }
        public B withPolicy(String policy) {
            config().policy = policy;
            return self();
        }
        public B withAgentType(String agent_type) {
            config().agent_type = agent_type;
            return self();
        }
    }

    private static class TetherBuilder extends Builder<Tether, Config, TetherBuilder> {
        private Config config = new Config();
        @Override protected Config config() { return config; }
        @Override protected TetherBuilder self() { return this; }
        public Tether create() {
            Config config = this.config;
            this.config = null;
            return new Tether(config);
        }
    }

    private static Config validate(Config config) {
        if (config.address == null)
            throw new IllegalArgumentException("Address is required");
        if (config.directory == null)
            config.directory = String.format("//%1s/directory", new Address(config.address).getHost());
        return config;
    }

    public static Builder<?,?,?> Builder() {
        return new TetherBuilder();
    }

    private final Config config;
    private final Sender sender;

    protected Tether(Config config) {
        this.config = validate(config);
        this.sender = makeSender();
    }

    public Tether(String directory, String address, String redirect_target,
            String host, String port, String policy, String agent_type) {
        config = new Config();
        config.directory = directory;
        config.address = address;
        config.redirect_target = redirect_target;
        config.host = host;
        config.port = port;
        config.policy = policy;
        config.agent_type = agent_type;
        validate(config);
        this.sender = makeSender();
    }

    private Sender makeSender() {
        return Sender.Builder().withTarget(config.directory).withHandlers(this).create();
    }

    private String getAgent() {
        if (config.agent_type != null) {
            return String.format("//%1s/agents/%2s-%3s", new Address(config.directory).getHost(), config.host, config.port);
        } else {
            return null;
        }
    }

    @Override
    public void onLinkRemoteOpen(Event event) {
        Message msg = Message.Factory.create(); // XXX: why not cached message?
        Map<String, String> properties = new HashMap<String, String>();
        properties.put("opcode", "route");
        msg.setApplicationProperties(new ApplicationProperties(properties));
        List<Object> body = new ArrayList<Object>();
        msg.setBody(new AmqpSequence(body));
        body.add(config.address);
        List<String> tuple = new ArrayList<String>(); {
            tuple.add(config.host);
            tuple.add(config.port);
            tuple.add(config.redirect_target);
        }
        body.add(tuple);
        body.add(null);
        sender.send(msg);
        String agent = getAgent();
        if (agent != null) {
            body.set(0, agent);
            tuple.set(2, null);
            sender.send(msg);
        }
    }

    public void start(Reactor reactor) {
        sender.start(reactor);
    }

    public void stop(Reactor reactor) {
        sender.stop(reactor);
    }
}
