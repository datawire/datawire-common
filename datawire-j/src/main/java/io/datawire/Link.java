/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Map;
import java.util.logging.Logger;

import org.apache.qpid.proton.amqp.Binary;
import org.apache.qpid.proton.amqp.Symbol;
import org.apache.qpid.proton.amqp.messaging.Source;
import org.apache.qpid.proton.amqp.messaging.Target;
import org.apache.qpid.proton.amqp.transport.AmqpError;
import org.apache.qpid.proton.amqp.transport.ErrorCondition;
import org.apache.qpid.proton.amqp.transport.LinkError;
import org.apache.qpid.proton.engine.Connection;
import org.apache.qpid.proton.engine.EndpointState;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.Sender;
import org.apache.qpid.proton.engine.Session;
import org.apache.qpid.proton.reactor.Reactor;

abstract class Link extends BaseHandler {
    private static final Logger log = Logger.getLogger(Link.class.getName());
    public static final Symbol UNAVAILABLE = Symbol.getSymbol("datawire:link:unavailable");
    private static final Symbol NETWORK_HOST = Symbol.getSymbol("network-host");
    private static final Symbol NETWORK_PORT = Symbol.getSymbol("port");
    private static final Symbol NETWORK_ADDRESS = Symbol.getSymbol("address");

    public static class Config {
        String source;
        String target;
        ArrayList<Handler> handlers = new ArrayList<Handler>();

        @Override
        public int hashCode() {
            final int prime = 31;
            int result = 1;
            result = prime * result
                    + ((handlers == null) ? 0 : handlers.hashCode());
            result = prime * result
                    + ((source == null) ? 0 : source.hashCode());
            result = prime * result
                    + ((target == null) ? 0 : target.hashCode());
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
            if (handlers == null) {
                if (other.handlers != null)
                    return false;
            } else if (!handlers.equals(other.handlers))
                return false;
            if (source == null) {
                if (other.source != null)
                    return false;
            } else if (!source.equals(other.source))
                return false;
            if (target == null) {
                if (other.target != null)
                    return false;
            } else if (!target.equals(other.target))
                return false;
            return true;
        }
    }

    protected abstract static class Builder<S extends Link, C extends Config, B extends Builder<S,C,B>> {
        protected abstract C config();
        protected abstract B self();
        public abstract S create();

        public B withTarget(String target) {
            config().target = target;
            return self();
        }
        public B withSource(String source) {
            config().source = source;
            return self();
        }
        public B withHandlers(Handler... handlers) {
            config().handlers.addAll(Arrays.asList(handlers));
            return self();
        }
    }

    public static Builder<?,?,?> Builder() { return null; }

    /**
     * create a link either a Sender or Receiver
     * @author bozzo
     *
     */
    protected interface LinkCreator {
        org.apache.qpid.proton.engine.Link create(Reactor reactor);
    }

    private org.apache.qpid.proton.engine.Link _link;
    private Object trace; // TODO
    private boolean relink;

    protected org.apache.qpid.proton.engine.Link get_link() {
        return _link;
    }

    /**
     * 
     * @return subclass specific {@link LinkCreator}
     */
    protected abstract LinkCreator getLinkCreator();

    protected Link(Config config) {
        for (Handler handler : config.handlers)
            add(handler);
    }
    protected Link(org.apache.qpid.proton.engine.Handler... handlers) {
        if (handlers != null) {
            for (Handler handler : handlers)
                add(handler);
        }
    }

    public void start(Reactor reactor) {
        start(reactor, null, true);
    }

    protected void start(Reactor reactor, LinkCreator link) {
        start(reactor, link, true);
    }

    protected void start(Reactor reactor, boolean open) {
        start(reactor, null, open);
    }

    private void start(Reactor reactor, LinkCreator link, boolean open) {
        if (link == null)
            link = this.getLinkCreator();
        _link = link.create(reactor);
        _link.open();
        _link.getSession().open();
        if (open)
            _link.getSession().getConnection().open();
        setHandler(_link.getSession().getConnection(), this); // XXX: do we need this? see _session() below
    }

    public void stop(Reactor reactor) {
        if (_link != null)
            _link.close();
    }

    public boolean getLinked() {
        return  _link != null &&
                _link.getLocalState() == EndpointState.ACTIVE &&
                _link.getRemoteState() == EndpointState.ACTIVE;
    }

    @Override
    public void onLinkFlow(Event event) {
        do_drained(event);
    }

    private void do_drained(Event event) {
        org.apache.qpid.proton.engine.Link link = event.getLink();
        if (link != _link)
            return;
        if (link.getDrain() && link.getCredit() == 0)
            event.redispatch(io.datawire.Event.Type.DRAINED, this);
    }

    @Override
    public void onDelivery(Event event) {
        event.delegate();
        do_drained(event);
    }

    @Override
    public void onLinkLocalClose(Event event) {
        org.apache.qpid.proton.engine.Link link = event.getLink();
        if (link == _link && link.getRemoteState() != EndpointState.CLOSED) {
            link.getSession().close();
            link.getSession().getConnection().close();
            if (!needRelink())
                _link = null;
        }
    }

    public boolean needRelink() {
        // TODO: Stream sets _relink on links, check that.
        return false;
    }

    @Override
    public void onLinkRemoteClose(Event event) {
        org.apache.qpid.proton.engine.Link link = event.getLink();
        link.close();
        event.getSession().close();
        event.getConnection().close();
        LinkCreator rlink = redirect(link);
        if (rlink != null) {
            log.fine(String.format("Redirecting to %s", rlink));
            start(event.getReactor(), rlink);
        } else if (link.getRemoteCondition() != null) {
            ErrorCondition remoteCondition = link.getRemoteCondition();
            if (remoteCondition.getCondition() == null) {
                // ok
            } else if (remoteCondition.getCondition() == UNAVAILABLE) {
                log.info("target address unavailable");
            } else {
                log.warning(String.format("unexpected remote close condition: %s", remoteCondition));
                if (link == _link)
                    _link = null;
            }
        }
    }

    private LinkCreator redirect(org.apache.qpid.proton.engine.Link link) {
        ErrorCondition remoteCondition = link.getRemoteCondition();
        if (remoteCondition != null && remoteCondition.getCondition() == LinkError.REDIRECT) {
            Map info = remoteCondition.getInfo();
            String host = getInfo(info, NETWORK_HOST);
            String port = getInfo(info, NETWORK_PORT);
            final Address address = Address.parse(getInfo(info, NETWORK_ADDRESS));
            final String network = String.format("%1s:%2s", host, port);
            final String pretty;
            if (address != null && address.getNetwork() != null) {
                pretty = address.getText();
            } else {
                pretty = String.format("%1s, %2s", network, address);
            }
            return new LinkCreator() {
                @Override
                public org.apache.qpid.proton.engine.Link create(Reactor reactor) {
                    org.apache.qpid.proton.engine.Link link = getLinkCreator().create(reactor);
                    link.getSession().getConnection().setHostname(network);
                    if (address != null) {
                        if (link instanceof Sender) {
                            setLinkTarget(link, address.getText());
                        } else {
                            setLinkSource(link, address.getText());
                        }
                    }
                    return link;
                }

                @Override
                public String toString() {
                    return pretty;
                }
            };
        } else {
            return null;
        }
    }
    private final Charset UTF8_CHARSET = Charset.forName("UTF-8");
    private String getInfo(Map info, Symbol key) {
        if (info == null || key == null)
            return null;
        Object value = info.get(key);
        if (value instanceof String) {
            return (String) value;
        } else if (value instanceof Binary) {
            Binary binary = (Binary)value;
            return new String(binary.getArray(), UTF8_CHARSET);
        }
        return null;
    }

    @Override
    public void onConnectionBound(Event event) {
        event.getTransport().setIdleTimeout(60000); /// XXX: units???
        // TODO: transport tracer
    }

    @Override
    public void onConnectionUnbound(Event event) {
        if (_link != null && _link.getSession().getConnection() == event.getConnection()) {
            String relink;
            if (needRelink()) {
                relink = " (relink)";
            } else {
                relink = "";
            }
            log.info(String.format("reconnecting... to %1s%2s", getNetwork(), relink));
            Reactor reactor = event.getReactor();
            start(reactor, false);
            reactor.schedule(1, new BaseHandler() {
                @Override
                public void onTimerTask(Event event) {
                    if (_link != null) {
                        _link.getSession().getConnection().open();
                    }
                }
            });
        }
    }

    protected abstract String getNetwork();

    @Override
    public void onTransportError(Event event) {
        ErrorCondition cond = event.getTransport().getCondition();
        String err = String.format("transport error %1s: %2s", cond.getCondition(), cond.getDescription());
        if (cond.getCondition() == AmqpError.RESOURCE_LIMIT_EXCEEDED &&
                cond.getDescription() == "local-idle-timeout expired") {
            log.info(err);
        } else {
            log.severe(err);
        }
    }

    @Override
    public void onTransportClosed(Event event) {
        event.getConnection().free();
    }

    protected Session _session(Reactor reactor) {
        Connection conn = reactor.connection(this);
        conn.setHostname(getNetwork());
        return conn.session();
    }

    protected void setLinkSource(org.apache.qpid.proton.engine.Link link, String source) {
        Source src = new Source();
        src.setAddress(source);
        link.setSource(src);
    }

    protected void setLinkTarget(org.apache.qpid.proton.engine.Link link, String target) {
        Target tgt = new Target();
        tgt.setAddress(target);
        link.setTarget(tgt);
    }
}
