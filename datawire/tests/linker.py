# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from proton import EventType, Message
from proton.reactor import Reactor
from proton.handlers import CHandshaker
from datawire import Linker, Processor, Receiver, Sender, Stream

class Sink(Processor):

    def __init__(self):
        Processor.__init__(self)
        self.messages = []

    def on_message(self, event):
        msg = event.message
        self.messages.append(msg.body)

PORT = 5678

OPENED = EventType("opened")
CLOSED = EventType("closed")

class Closer:

    def __init__(self, delegate, closer):
        self.delegate = delegate
        self.closer = closer

    def on_connection_bound(self, event):
        event.dispatch(self.delegate)
        event.dispatch(self.closer, OPENED)

    def on_connection_unbound(self, event):
        event.dispatch(self.delegate)
        event.dispatch(self.closer, CLOSED)

    def on_unhandled(self, name, event):
        event.dispatch(self.delegate)

class Server:

    def __init__(self, delegate):
        self.delegate = delegate
        self.acceptor = None
        self.opened = 0
        self.closed = 0
        self.max_connections = None

    def on_opened(self, event):
        self.opened += 1

    def on_closed(self, event):
        self.closed += 1
        if self.max_connections is not None and self.closed >= self.max_connections:
            self.acceptor.close()

    def on_reactor_init(self, event):
        self.acceptor = event.reactor.acceptor("localhost", PORT, Closer(self.delegate, self))

class SinkTest:

    def __init__(self):
        self.sink = Sink()
        self.server = Server(self.sink)
        self.reactor = Reactor(self.server)

    def testSender(self, count=1):
        self.server.max_connections = 1
        snd = Sender("//localhost:%s" % PORT)
        self.reactor.handler.add(snd)
        snd.start(self.reactor)
        for i in range(count):
            snd.send("test-%s" % i)
        snd.close()
        self.reactor.run()
        for i in range(count):
            assert self.sink.messages[i] == "test-%s" % i, self.sink.messages[i]

    def testSender4K(self):
        self.testSender(4*1024)

    def testLinker(self, address_count=1, message_count=1):
        self.server.max_connections = address_count
        linker = Linker()
        linker.start(self.reactor)
        for i in range(address_count):
            for j in range(message_count):
                snd = linker.sender("//localhost:%s/%s" % (PORT, i))
                assert len(linker.senders) == i + 1
                snd.send("test-%s-%s" % (i, j))
        linker.close()
        self.reactor.run()

        # XXX: The ordering happens to work out here due to
        # implementation constraints, however strictly speaking the
        # messages captured by the sink are only partially ordered.
        idx = 0
        for i in range(address_count):
            for j in range(message_count):
                assert self.sink.messages[idx] == "test-%s-%s" % (i, j)
                idx += 1

    def testLinker2A1M(self):
        self.testLinker(2, 1)

    def testLinker4A1M(self):
        self.testLinker(4, 1)

    def testLinker16A1M(self):
        self.testLinker(16, 1)

    def testLinker1A2M(self):
        self.testLinker(1, 2)

    def testLinker1A4M(self):
        self.testLinker(1, 4)

    def testLinker1A16M(self):
        self.testLinker(1, 16)

    def testLinker2A2M(self):
        self.testLinker(2, 2)

    def testLinker4A4M(self):
        self.testLinker(4, 4)

    def testLinker16A16M(self):
        self.testLinker(16, 16)


class Source:

    def __init__(self, template="test-%s", start=0, limit=None, window=1024):
        self.template = template
        self.count = start
        self.limit = limit
        self.window = window
        self.message = Message()
        self.handlers = [CHandshaker()]

    def on_link_flow(self, event):
        if event.sender:
            self.pump(event.sender)

    def pump(self, snd):
        while self.count != self.limit and snd.credit > 0 and snd.queued < self.window:
            self.message.body = self.template % self.count
            dlv = snd.send(self.message)
            dlv.settle()
            self.count += 1

class SourceTest:

    def __init__(self):
        self.source = Source("test-%s")
        self.server = Server(self.source)
        self.reactor = Reactor(self.server)

    def testReceiver(self, count=1):
        self.server.max_connections = 1
        self.source.limit = count

        oself = self

        class Counter:
            def __init__(self):
                self.received = 0
                self.receiver = None
            def on_message(self, event):
                assert event.message.body == oself.source.template % self.received
                self.received += 1
                if self.received == count:
                    self.receiver.stop(event.reactor)

        counter = Counter()
        rcv = Receiver("//localhost:%s" % PORT, Processor(counter))
        counter.receiver = rcv
        self.reactor.handler.add(rcv)
        rcv.start(self.reactor)
        self.reactor.run()
        assert counter.received == count

    def testReceiver150(self):
        self.testReceiver(150)

    # This doesn't seem to work for any value > 150! This is a proton
    # bug that needs to be isolated and pushed upstream. Enable and
    # run under valgrind for more details.
    def XXXtestReceiver151(self):
        self.testReceiver(151)
