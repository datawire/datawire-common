import sys
from common import *
from fnmatch import fnmatch

class Tether(Handler):

    def __init__(self, director, host, port):
        self.director = director
        self.host = host
        self.port = port

    def on_start(self, drv):
        self.driver = drv
        self.connect()

    def on_transport_closed(self, event):
        conn = event.context.connection
        self.conn = None
        self.driver.schedule(self.connect, 1)

    def connect(self):
        self.conn = self.driver.connection(self)
        self.conn.hostname = self.director
        self.conn.properties = {symbol("compute-node"): (self.host, self.port)}
        self.conn.open()

class Updater(Handler):

    def __init__(self, delegate):
        self.__delegate = delegate
        self.serial = 0
        self.handlers = [FlowController(1024), Handshaker(), self]
        self.message = Message()
        self.trace = True
        self.outgoing = []

    def log(self, msg, *args):
        if self.trace:
            sys.stderr.write(("%s\n" % msg) % args)
            sys.stderr.flush()

    def on_link_remote_open(self, event):
        link = event.context
        if link.is_sender:
            self.log("adding link: %s", link)
            link.serial = self.serial
            self.outgoing.append(link)

    def on_link_final(self, event):
        link = event.context
        if link.is_sender:
            self.log("removing link: %s", link)
            self.outgoing.remove(link)
            del link.serial

    def on_link_flow(self, event):
        link = event.context
        if link.is_sender and link.credit:
            self.push(link)

    def push(self, snd):
        if not hasattr(snd, "serial"):
            self.log("warning, no serial %s", snd)
            return
        if snd.serial == self.serial: return
        self.log("updating %s to %s" , snd, self.serial)
        self.message.clear()
        self.message.body = self.__delegate.update()
        dlv = snd.delivery("serial-%s" % self.serial)
        snd.send(self.message.encode())
        dlv.settle()
        snd.serial = self.serial
        self.log("Sent: %r", self.message)
        self.message.clear()

    def updated(self):
        self.serial += 1
        for snd in self.outgoing:
            self.push(snd)

class Interceptor(Handler):

    def __init__(self, pattern, *delegates):
        self.pattern = pattern
        self.delegates = expand(delegates)

    def on_start(self, drv):
        for h in self.delegates:
            dispatch(h, "on_start", drv)

    def on_link_remote_open(self, event):
        if event.link.is_sender:
            address = event.link.remote_source.address
        else:
            address = event.link.remote_target.address

        if address and fnmatch(address, self.pattern):
            event.link.handlers = self.delegates
            for h in event.link.handlers:
                event.dispatch(h)

class Controller(Handler):

    def __init__(self, delegate):
        self.delegate = delegate
        self.updater = Updater(delegate)
        self.decoder = MessageDecoder(self)
        self.handlers = [self.updater, self.decoder]

    def on_message(self, rcv, msg):
        print "CONTROL:", msg
        if msg.properties:
            opcode = msg.properties.get("opcode")
            if opcode:
                self.dispatch(opcode, msg)
                self.updater.updated()

    def dispatch(self, opcode, msg):
        print "DISPATCH:", self.delegate
        dispatch(self.delegate, "on_%s" % opcode, msg)

class Service(Handler):

    def __init__(self, director, host, port, trace=None):
        self.host = host
        self.port = port
        self.trace = trace
        self.decoder = MessageDecoder(self)
        self.controller = Controller(self)
        self.router = Router()
        self.handlers = [Interceptor("*/controller", self.controller), FlowController(1024), Handshaker(),
                         self.decoder, self.router, self]
        self.tether = Tether(director, host, port)

    def on_start(self, drv):
        drv.acceptor(self.host, self.port)
        self.tether.on_start(drv)

    def on_transport_closed(self, event):
        event.connection.free()
        event.transport.unbind()

    def route(self, msg):
        row = self.router.outgoing(msg.address)
        if row:
            for link in row:
                dlv = link.delivery("")
                link.send(msg.encode())
                dlv.settle()
        else:
            print "NO ROUTE:", msg
