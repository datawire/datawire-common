# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

import logging
from proton import DELEGATED, Endpoint, EventType, Message
from .address import Address

log = logging.getLogger(__name__)

def redirect(link, original):
    if link.remote_condition and link.remote_condition.name == "amqp:link:redirect":
        info = link.remote_condition.info
        # XXX: should default these based on "//" address
        host = info.get("network-host", None)
        port = info.get("port", None)

        address = Address.parse(info.get("address", None))
        network = "%s:%s" % (host, port)

        if address and address.network:
            pretty = address.text
        else:
            pretty = "%s, %s" % (network, address)

        class Redirect:

            def __call__(self, reactor):
                link = original(reactor)
                link.session.connection.hostname = network
                if address:
                    if link.is_sender:
                        link.target.address = address.text
                    else:
                        link.source.address = address.text
                return link

            def __str__(self):
                return pretty

        return Redirect()
    else:
        return None

DRAINED = EventType("drained")

class Link:

    def __init__(self, *handlers, **kwargs):
        self.handlers = handlers
        self._link = None
        self.trace = None

    def start(self, reactor, link=None, open=True):
        if link is None:
            link = self.link
        self._link = link(reactor)
        self._link.open()
        self._link.session.open()
        if open:
            self._link.session.connection.open()
        self._link.session.connection.handler = self

    def stop(self, reactor):
        if self._link:
            self._link.close()

    @property
    def linked(self):
        return (self._link.state & Endpoint.LOCAL_ACTIVE and self._link.state & Endpoint.REMOTE_ACTIVE)

    def on_link_flow(self, event):
        self.do_drained(event)

    def on_delivery(self, event):
        for h in self.handlers:
            event.dispatch(h)
        self.do_drained(event)
        return DELEGATED

    def do_drained(self, event):
        link = event.link
        if link != self._link: return
        if link.drain_mode and link.credit == 0:
            event.dispatch(self, DRAINED)

    def on_link_local_close(self, event):
        link = event.link
        if link == self._link and not link.state & Endpoint.REMOTE_CLOSED:
            link.session.close()
            link.connection.close()
            if not (hasattr(self._link, "_relink") and self._link._relink):
                self._link = None

    def on_link_remote_close(self, event):
        link = event.link
        link.close()
        event.session.close()
        event.connection.close()
        rlink = redirect(event.link, self.link)
        if rlink:
            log.debug("redirecting to %s", rlink)
            self.start(event.reactor, rlink)
        elif link.remote_condition:
            if link.remote_condition.name == "datawire:link:unavailable":
                log.info("target address unavailable")
            else:
                log.warning("unexpected remote close condition: %s", link.remote_condition)
                if link == self._link:
                    self._link = None

    def log_proton_output(self, transport, output):
        # str(transport) looks like "<proton.Transport 0x104186e50 ~ 0x7fd3d0ceec70>"
        log.warning("PROTON:%s", output)

    def on_connection_bound(self, event):
        event.transport.idle_timeout = 60.0
        event.transport.tracer = self.log_proton_output
        if self.trace is not None:
            event.transport.trace(self.trace)

    def on_connection_unbound(self, event):
        if self._link and self._link.connection == event.connection:
            if hasattr(self._link, "_relink") and self._link._relink:
                relink = " (relink)"
            else:
                relink = ""
            log.info("reconnecting... to %s%s", self.network(), relink)
            self.start(event.reactor, open=False)
            class Open:
                def on_timer_task(_self, event):
                    if self._link:
                        self._link.connection.open()
            event.reactor.schedule(1, Open())

    def on_transport_error(self, event):
        cond = event.transport.condition
        log.error("transport error %s: %s", cond.name, cond.description)

    def on_transport_closed(self, event):
        event.connection.free()

    def _session(self, reactor):
        conn = reactor.connection()
        conn.hostname = self.network()
        return conn.session()

class Sender(Link):

    def __init__(self, target, *handlers, **kwargs):
        Link.__init__(self, *handlers)
        self.target = target
        self.source = kwargs.pop("source", None)
        self.__message = Message()
        self.__buffer = []
        self.__closed = False
        if kwargs: raise TypeError("unrecognized keyword arguments: %s" % ", ".join(kwargs.keys()))

    def network(self):
        return Address(self.target).network

    def link(self, reactor):
        ssn = self._session(reactor)
        snd = ssn.sender("%s->%s" % (self.source, self.target))
        snd.source.address = self.source
        snd.target.address = self.target
        return snd

    def on_link_flow(self, event):
        self.__pump(event.link)
        Link.on_link_flow(self, event)

    def __pump(self, link):
        while self.__buffer and link.credit:
            dlv = link.delivery(link.delivery_tag())
            link.send(self.__buffer.pop(0))
            dlv.settle()
        if self.__closed and not self.__buffer:
            link.close()

    def send(self, o):
        if self._link is None:
            raise ValueError("link is not started")
        if isinstance(o, Message):
            self.__buffer.append(o.encode())
            self.__pump(self._link)
        else:
            self.__message.body = o
            return self.send(self.__message)

    def close(self):
        self.__closed = True

class Receiver(Link):

    def __init__(self, source, *handlers, **kwargs):
        Link.__init__(self, *handlers)
        self.source = source
        self.target = kwargs.pop("target", None)
        self.drain = kwargs.pop("drain", None)
        if kwargs: raise TypeError("unrecognized keyword arguments: %s" % ", ".join(kwargs.keys()))

    def network(self):
        return Address(self.source).network

    def link(self, reactor):
        ssn = self._session(reactor)
        rcv = ssn.receiver("%s->%s" % (self.source, self.target))
        if self.drain:
            rcv.drain_mode = self.drain
        rcv.source.address = self.source
        rcv.target.address = self.target
        return rcv

class Tether(Sender):

    def __init__(self, directory, address, target, host=None, port=None, policy=None, agent_type=None):
        if directory is None:
            directory = u"//%s/directory" % Address(address).host
            log.debug("Tether picking default directory %r from in_address %r", directory, address)
        else:
            directory = unicode(directory)
        Sender.__init__(self, directory)
        self.directory = directory
        self.address = unicode(address)
        self.redirect_target = target
        self.host = host
        self.port = port
        self.policy = policy
        self.agent_type = unicode(agent_type)
        if agent_type:
            self.agent = u"//%s/agents/%s-%s" % (Address(self.directory).host, self.host, self.port)
        else:
            self.agent = None

    def on_link_local_open(self, event):
        msg = Message()
        msg.properties = {u"opcode": "route"}
        msg.body = (self.address, (self.host, self.port, self.redirect_target), None)
        if self.policy:
            msg.body += (self.policy,)
        msg.send(event.link)
        if self.agent:
            msg.body = (self.agent, (self.host, self.port, None), None)
            msg.send(event.link)

def _key(target, handlers, kwargs):
    items = kwargs.items()
    items.sort()
    return target, handlers, tuple(items)

class Linker:

    def __init__(self):
        self.senders = {}
        self.reactor = None
        self.started = False

    def start(self, reactor):
        self.reactor = reactor
        for snd in self.senders.values():
            snd.start(reactor)
        self.started = True

    def stop(self, reactor):
        for snd in self.senders.values():
            snd.stop(reactor)
        self.started = False

    def sender(self, target, *handlers, **kwargs):
        key = _key(target, handlers, kwargs)
        if key in self.senders:
            snd = self.senders[key]
        else:
            snd = Sender(target, *handlers, **kwargs)
            self.senders[key] = snd
            if self.started:
                snd.start(self.reactor)
        return snd

    def close(self):
        for snd in self.senders.values():
            snd.close()
