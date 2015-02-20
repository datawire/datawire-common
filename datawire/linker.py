# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited. 

from proton import DELEGATED, Endpoint, EventType, Message
from .address import Address

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

class Linker:

    def __init__(self, *handlers, **kwargs):
        self.handlers = handlers
        self._link = None

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
            self._link = None

    def on_link_remote_close(self, event):
        link = event.link
        link.close()
        event.session.close()
        event.connection.close()
        rlink = redirect(event.link, self.link)
        if rlink:
            print "redirecting to %s" % rlink
            self.start(event.reactor, rlink)
        elif link.remote_condition:
            print link.remote_condition
            if link == self._link:
                self._link = None

    def on_connection_bound(self, event):
        event.transport.idle_timeout = 60.0

    def on_connection_unbound(self, event):
        if self._link and self._link.connection == event.connection:
            print "reconnecting... to %s" % self.network()
            self.start(event.reactor, open=False)
            class Open:
                def on_timer_task(_self, event):
                    self._link.connection.open()
            event.reactor.schedule(1, Open())

    def on_transport_error(self, event):
        cond = event.transport.condition
        print "%s: %s" % (cond.name, cond.description)

    def on_transport_closed(self, event):
        event.connection.free()

    def _session(self, reactor):
        conn = reactor.connection()
        conn.hostname = self.network()
        return conn.session()

class Sender(Linker):

    def __init__(self, target, *handlers, **kwargs):
        Linker.__init__(self, *handlers)
        self.target = target
        self.source = kwargs.pop("source", None)
        if kwargs: raise TypeError("unrecognized keyword arguments: %s" % ", ".join(kwargs.keys()))

    def network(self):
        return Address(self.target).network

    def link(self, reactor):
        ssn = self._session(reactor)
        snd = ssn.sender("%s->%s" % (self.source, self.target))
        snd.source.address = self.source
        snd.target.address = self.target
        return snd

class Receiver(Linker):

    def __init__(self, source, *handlers, **kwargs):
        Linker.__init__(self, *handlers)
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

    def __init__(self, directory, address, target):
        Sender.__init__(self, directory)
        self.address = address
        self.redirect_target = target

    def on_link_local_open(self, event):
        msg = Message()
        msg.properties = {u"opcode": "route"}
        msg.body = (self.address, (None, None, self.redirect_target), None)
        msg.send(event.link)
