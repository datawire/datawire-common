# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from proton import EventType, Message
from proton.handlers import CHandshaker
from datawire import Processor

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

class Timeout:
    _cancelled = None
    _timer = None

    def set_timeout(self, reactor, timeout):
      assert not self._timer, "Timeout is already set"
      self._timer = reactor.schedule(timeout, self)
      self.cancelled = False

    def cancel(self):
        assert self._timer, "Cannot cancel when timeout is not set"
        self._timer.cancel()
        self._timer = None
        self.cancelled = True

    @property
    def cancelled(self):
      return self._cancelled
