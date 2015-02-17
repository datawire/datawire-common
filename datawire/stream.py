from proton import Message, Endpoint
from proton.reactor import Reactor
from proton.handlers import CFlowController, CHandshaker

class Entry:

    def __init__(self, msg):
        self.message = msg

class Store:

    def __init__(self):
        self.serial = 0
        self.entries = []
        self.readers = []
        self.lastgc = 0

    def start(self):
        return self.min()

    def put(self, msg):
        self.entries.append(Entry(msg))

    def max(self):
        return self.serial + len(self.entries)

    def min(self):
        return self.serial

    def get(self, serial):
        return self.entries[serial - self.serial]

    def gc(self):
        serial = self.max()
        for r in self.readers:
            serial = min(r.serial, serial)

        if serial == self.lastgc:
            return

        if self.serial < serial:
            delta = serial - self.serial
            tail = self.compact(self.entries[:delta])
            self.entries[:delta] = tail
            self.serial += delta - len(tail)

        self.lastgc = serial

    def compact(self, tail):
        return []

    def reader(self):
        reader = Reader(self)
        self.readers.append(reader)
        return reader

class Reader:

    def __init__(self, store):
        self.store = store
        self.serial = store.min()

    def next(self):
        if self.more():
            result = self.store.get(self.serial)
            self.serial += 1
            return result
        else:
            return None

    def more(self):
        return self.serial < self.store.max()

    def close(self):
        self.store.readers.remove(self)

class Stream:

    def __init__(self, store = None):
        self.history = Store()
        self.store = store or Store()
        self.handlers = [CFlowController(), CHandshaker()]
        self.outgoing = []
        self.message = Message()
        self.closed = False

    def put(self, msg):
        if isinstance(msg, Message):
            self.store.put(msg.encode())
        else:
            self.message.body = msg
            self.store.put(self.message.encode())

    def close(self):
        self.closed = True

    def on_link_local_open(self, event):
        self.setup(event)

    def on_link_remote_open(self, event):
        self.setup(event)

    def setup(self, event):
        snd = event.sender
        if snd and not hasattr(snd, "reader"):
            snd.reader = self.store.reader()
            self.outgoing.append(snd)

    def on_link_final(self, event):
        if event.sender:
            event.sender.reader.close()
            self.outgoing.remove(event.sender)

    def on_link_flow(self, event):
        if event.sender:
            self.pump_sender(event.sender)

    def pump_sender(self, snd):
        while snd.reader.more() and snd.credit > 0 and snd.queued < 1024:
            entry = snd.reader.next()
            dlv = snd.delivery(snd.delivery_tag())
            snd.send(entry.message)
            dlv.settle()
        if not snd.reader.more():
            snd.drained()
            if self.closed:
                snd.close()

    def pump(self):
        for snd in self.outgoing:
            self.pump_sender(snd)
        self.store.gc()

    def on_reactor_quiesced(self, event):
        self.pump()

    def on_delivery(self, event):
        rcv = event.receiver
        dlv = event.delivery
        if rcv and not dlv.partial:
            msg = rcv.recv(dlv.pending)
            self.store.put(msg)
            dlv.settle()
