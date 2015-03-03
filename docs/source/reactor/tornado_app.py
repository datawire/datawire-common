#!/usr/bin/python

import tornado.ioloop
from proton.reactor import Reactor
from proton.handlers import IOHandler

class TornadoApp:

    def __init__(self, *args):
        self.reactor = Reactor(*args)
        self.reactor.global_handler = self
        self.io = IOHandler()
        self.loop = tornado.ioloop.IOLoop.instance()
        self.count = 0
        self.reactor.start()
        self.reactor.process()

    def on_reactor_quiesced(self, event):
        event.reactor.yield_()

    def on_unhandled(self, name, event):
        event.dispatch(self.io)

    def _events(self, sel):
        events = self.loop.ERROR
        if sel.reading:
            events |= self.loop.READ
        if sel.writing:
            events |= self.loop.WRITE
        return events

    def _schedule(self, sel):
        if sel.deadline:
            self.loop.add_timeout(sel.deadline, lambda: self.expired(sel))

    def _expired(self, sel):
        sel.expired()

    def _process(self):
        self.reactor.process()
        if not self.reactor.quiesced:
            self.loop.add_callback(self._process)

    def _callback(self, sel, events):
        if self.loop.READ & events:
            sel.readable()
        if self.loop.WRITE & events:
            sel.writable()
        self._process()

    def on_selectable_init(self, event):
        sel = event.context
        if sel.fileno() >= 0:
            self.loop.add_handler(sel.fileno(), lambda fd, events: self._callback(sel, events), self._events(sel))
        self._schedule(sel)
        self.count += 1

    def on_selectable_updated(self, event):
        sel = event.context
        if sel.fileno() > 0:
            self.loop.update_handler(sel.fileno(), self._events(sel))
        self._schedule(sel)

    def on_selectable_final(self, event):
        sel = event.context
        if sel.fileno() > 0:
            self.loop.remove_handler(sel.fileno())
        sel.release()
        self.count -= 1
        if self.count == 0:
            self.loop.add_callback(self._stop)

    def _stop(self):
        self.reactor.stop()
        self.loop.stop()
