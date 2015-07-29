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

public class Tether extends Sender {
    protected static class Config extends Sender.Config {
        public String directory;
        public String address;
        public String redirect_target;
        public String host;
        public String port;
        public String policy;
        public String agent_type;
    }

    public static class Builder {
        private Config config = new Config();
        public Sender create() {
            Config config = this.config;
            this.config = null;
            return new Tether(config);
        }
    }

    private final Config config;
    
    protected Tether(Config config) {
        super(config);
        this.config = config;
    }
    
    public static Builder Builder() {
        return new Builder();
    }
    
    public Tether(String directory, String address, String redirect_target,
            String host, String port, String policy, String agent_type) {
        super(defaultDirectory(directory, address), null);
        config = new Config();
        config.directory = defaultDirectory(directory, address);
        config.address = address;
        config.redirect_target = redirect_target;
        config.host = host;
        config.port = port;
        config.policy = policy;
        config.agent_type = agent_type;
    }

    private String getAgent() {
        if (config.agent_type != null) {
            return String.format("//%1s/agents/%2s-%3s", new Address(config.directory).getHost(), config.host, config.port);
        } else {
            return null;
        }
    }

    private static String defaultDirectory(String directory, String address) {
        if (directory != null)
            return directory;
        else
            return String.format("//%1s/directory", new Address(address).getHost());
    }
    
    @Override
    public void onLinkLocalOpen(Event event) {
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
        send(msg);
        String agent = getAgent();
        if (agent != null) {
            body.set(0, agent);
            tuple.set(2, null);
            send(msg);
        }
    }
}
