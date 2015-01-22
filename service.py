import sys
import argparse
from common import *
from fnmatch import fnmatch

class Tether(Handler):

    def __init__(self, director, service, host, port, delegate=None):
        self.director = director
        self.service = service
        self.host = host
        self.port = port
        self.delegate = delegate

    def on_start(self, drv):
        self.driver = drv
        self.connect()

    def on_transport_closed(self, event):
        conn = event.context.connection
        self.conn = None
        self.driver.schedule(self.connect, 1)

    def on_connection_remote_open(self, event):
        if self.delegate:
            dispatch(self.delegate, "on_tether_connect", event)

    def connect(self):
        self.conn = self.driver.connection(self)
        self.conn.hostname = self.director
        self.conn.properties = {symbol("service"): (self.service, self.host, self.port)}
        self.conn.open()

class Updater(Handler, Logger):

    def __init__(self, delegate):
        self.__delegate = delegate
        self.serial = 0
        self.handlers = [FlowController(1024), Handshaker(), self]
        self.message = Message()
        self.outgoing = []

    @property
    def trace(self):
        return self.__delegate.trace

    def start(self, address):
        return self.serial

    def on_link_remote_open(self, event):
        link = event.context
        if link.is_sender:
            self.log("adding link: %s", link)
            link.serial = self.start(link.remote_source.address)
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
        self.update(snd)

    def update(self, snd):
        body = self.__delegate.update()
        if body is not None:
            self.message.clear()
            self.message.body = body
            dlv = snd.delivery("serial-%s" % self.serial)
            snd.send(self.message.encode())
            dlv.settle()
            self.log("Sent: %r", self.message)
            self.message.clear()
        snd.serial = self.serial

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

class Controller(Handler, Logger):

    def __init__(self, delegate):
        self.delegate = delegate
        self.updater = Updater(delegate)
        self.decoder = MessageDecoder(self)
        self.handlers = [self.updater, self.decoder]

    @property
    def trace(self):
        return self.delegate.trace

    def on_message(self, rcv, msg):
        self.log("CONTROL: %s", msg)
        if msg.properties:
            opcode = msg.properties.get("opcode")
            if opcode:
                self.dispatch(opcode, msg)
                self.updater.updated()

    def dispatch(self, opcode, msg):
        dispatch(self.delegate, "on_%s" % opcode, msg)

class Service(Handler, Logger):

    def __init__(self, director, service, host, port, trace=None, pubhost=None, pubport=None):
        self.host = host
        self.port = port
        self.trace = trace
        self.director = director
        self.decoder = MessageDecoder(self)
        self.controller = Controller(self)
        self.router = Router()
        self.send_queue_pool = SendQueuePool()
        self.handlers = [Interceptor("*/controller", self.controller), FlowController(1024), Handshaker(),
                         self.decoder, self.router, self]
        self.tether = Tether(director, service, pubhost or host, pubport or port, delegate=self)

    def update(self):
        return None

    def on_start(self, drv):
        drv.acceptor(self.host, self.port)
        self.tether.on_start(drv)
        self.send_queue_pool.on_start(drv)

    def on_transport_closed(self, event):
        event.connection.free()
        event.transport.unbind()

    def _redirect_rcv_snd(self, link, host="127.0.0.1", port="5672"):
        if link.is_sender:
            address = link.remote_source.address or link.remote_target.address
            row = self.router.incoming(address)
        else:
            address = link.remote_source.address or link.remote_target.address
            row = self.router.outgoing(address)
        if row is not None:
            for link2 in row:
                redirect_link(link2, host, port)
        redirect_link(link, host, port)

    def route(self, msg):
        row = self.router.outgoing(msg.address)
        if row:
            for link in row:
                dlv = link.delivery("")
                link.send(msg.encode())
                dlv.settle()
        else:
            if uid_pattern.match(msg.address) is not None:
                if not self.director:
                    raise IOError("Could not generate link to dynamic UID due to absence of a redirector.")
                new_address = "%s:://%s/dynamic" % (msg.address, self.director)
                msg.address = new_address
            # No existing route:  try to create one:
            self.send_queue_pool.to(msg.address).put(msg)

parser = argparse.ArgumentParser(description='Run deploy microservice.',
                                 add_help=False)
parser.add_argument('-u', '--host', default="localhost",
                    help='host interface on which to run microservice')
parser.add_argument('-p', '--port', type=int, default=5672,
                    help='host port on which to run microservice')
parser.add_argument('-r', '--redirector', default="localhost",
                    help='host of redirector (will only look on port 5672)')
parser.add_argument('--public-host', default=None,
                    help='public host which is used for applications to'
                    + ' access microservice')
parser.add_argument('--public-port', default=None,
                    help='public port which is used for applications to'
                    + ' access microservice')
parser.add_argument('-t', '--trace', action='store_true', default=False,
                    help='whether to display trace messages for debugging')


def get_base_argparser():
    return parser
