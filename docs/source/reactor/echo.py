#!/usr/bin/python

import sys, os
from proton.reactor import Reactor

class Echo:

    def __init__(self, source):
        self.source = source

    def on_selectable_init(self, event):
        sel = event.context

        # We can configure a selectable with any file descriptor we want.
        sel.fileno(self.source.fileno())
        # Ask to be notified when the file is readable.
        sel.reading = True
        event.reactor.update(sel)

    def on_selectable_readable(self, event):
        sel = event.context

        # The on_selectable_readable event tells us that there is data
        # to be read, or the end of stream has been reached.
        data = os.read(sel.fileno(), 1024)
        if data:
            print data,
        else:
            sel.terminate()
            event.reactor.update(sel)

class Program:

    def on_reactor_init(self, event):
        # Every selectable is a possible source of future events. Our
        # selectable stays alive until it reads the end of stream
        # marker. This will keep the whole reactor running until we
        # type Control-D.
        print "Type whatever you want and then use Control-D to exit:"
        event.reactor.selectable(Echo(sys.stdin))

r = Reactor(Program())
r.run()
