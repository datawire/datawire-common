from proton import DELEGATED, Endpoint, EventType

def redirect(link, original):
    if link.remote_condition and link.remote_condition.name == "amqp:link:redirect":
        info = link.remote_condition.info
        # XXX: should default these based on "//" address
        host = info.get("network-host", None)
        port = info.get("port", None)
        address = info.get("address", None)

        class Redirect:
            def link(self, reactor):
                link = original.link(reactor)
                link.session.connection.hostname = "%s:%s" % (host, port)
                if address:
                    if link.is_sender:
                        link.target.address = address
                    else:
                        link.source.address = address
                return link

            def __str__(self):
                return "%s => %s" % (original, (host, port, address))
        return Redirect()
    else:
        return None

class Config:

    def __init__(self, st):
        if "->" in st:
            self.sender = True
            self.source, self.target = st.split("->", 1)
        elif "<-" in st:
            self.sender = False
            self.target, self.source = st.split("<-", 1)
        else:
            raise ValueError(st)

        if self.source == "":
            self.source = None
        if self.target == "":
            self.target = None

    def __str__(self):
        if self.sender:
            return "%s->%s" % (self.source, self.target)
        else:
            return "%s<-%s" % (self.target, self.source)

    def _get_local(self):
        if self.sender:
            return self.source
        else:
            return self.target
    def _set_local(self, value):
        if self.sender:
            self.source = value
        else:
            self.target = value

    local = property(_get_local, _set_local)

    def _get_remote(self):
        if self.sender:
            return self.target
        else:
            return self.source
    def _set_remote(self, value):
        if self.sender:
            self.target = value
        else:
            self.source = value

    remote = property(_get_remote, _set_remote)

    @property
    def network(self):
        if self.remote is None: return None
        if self.remote.startswith("//"):
            return self.remote[2:].split("/", 1)[0]
        else:
            return None

    def link(self, reactor):
        conn = reactor.connection()
        conn.hostname = self.network
        ssn = conn.session()
        if self.sender:
            link = ssn.sender(str(self))
        else:
            link = ssn.receiver(str(self))
        link.source.address = self.source
        link.target.address = self.target
        return link

DRAINED = EventType("drained")

class Linker:

    def __init__(self, config, *handlers, **kwargs):
        if hasattr(config, "link"):
            self.config = config
        else:
            self.config = Config(config)
        self.handlers = handlers
        self.link = None
        self.on_drained = kwargs.pop("on_drained", None)
        if kwargs:
            raise TypeError("got unexpected keyword arg(s): %s" % ", ".join(kwargs.keys()))

    def start(self, reactor, config=None, open=True):
        if config is None:
            config = self.config
        self.link = config.link(reactor)
        if self.link.is_receiver and self.on_drained:
            self.link.drain_mode = True
        self.link.open()
        self.link.session.open()
        if open:
            self.link.session.connection.open()
        self.link.session.connection.handler = self

    def stop(self, reactor):
        if self.link:
            self.link.close()

    def on_link_flow(self, event):
        self.do_drained(event)

    def on_delivery(self, event):
        for h in self.handlers:
            event.dispatch(h)
        self.do_drained(event)
        return DELEGATED

    def do_drained(self, event):
        link = event.link
        if link != self.link: return
        if self.on_drained and link.drain_mode and link.credit == 0:
            event.dispatch(self, DRAINED)

    def on_link_local_close(self, event):
        link = event.link
        if link == self.link and not link.state & Endpoint.REMOTE_CLOSED:
            link.session.close()
            link.connection.close()
            self.link = None

    def on_link_remote_close(self, event):
        link = event.link
        link.close()
        event.session.close()
        event.connection.close()
        config = redirect(event.link, self.config)
        if config:
            print "redirecting to %s" % config
            self.start(event.reactor, config)
        elif link.remote_condition:
            print link.remote_condition
            if link == self.link:
                self.link = None

    def on_connection_bound(self, event):
        event.transport.idle_timeout = 60.0

    def on_connection_unbound(self, event):
        if self.link and self.link.connection == event.connection:
            print "reconnecting to %s" % self.config
            self.start(event.reactor, open=False)
            event.reactor.schedule(1, self)

    def on_transport_error(self, event):
        cond = event.transport.condition
        print "%s: %s" % (cond.name, cond.description)

    def on_transport_closed(self, event):
        event.connection.free()

    def on_timer_task(self, event):
        self.link.connection.open()
