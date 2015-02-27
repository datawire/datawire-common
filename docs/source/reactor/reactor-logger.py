#!/usr/bin/python

import time
from proton.reactor import Reactor

class Logger:

    def on_unhandled(self, name, event):
        print "LOG:", name, event

class Program:

    def on_reactor_init(self, event):
        print "Hello, World!"

    def on_reactor_final(self, event):
        print "Goodbye, World!"

r = Reactor(Program(), Logger())
r.run()

# Note that if you wanted to add the logger later, you could also
# write the above as below. All arguments to the reactor are just
# added to the default handler for the reactor.
def logging_enabled():
    return False

r = Reactor(Program())
if logging_enabled():
    r.handler.add(Logger())
r.run()
