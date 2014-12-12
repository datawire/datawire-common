from common import *

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

class Service(Handler):

    def __init__(self, director, host, port, trace=None):
        self.host = host
        self.port = port
        self.trace = trace
        self.decoder = MessageDecoder(self)
        self.handlers = [FlowController(1024), Handshaker(), self.decoder, self]
        self.tether = Tether(director, host, port)

    def on_start(self, drv):
        drv.acceptor(self.host, self.port)
        self.tether.on_start(drv)
