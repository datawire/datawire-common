#!/usr/bin/python

from proton.reactor import Reactor

class Program:

    # The reactor init event is produced by the reactor itself when it
    # starts.
    def on_reactor_init(self, event):
        print "Hello, World!"

# When you construct a reactor, you give it a handler.
r = Reactor(Program())

# When you call run, the reactor will process events. The reactor init
# event is what kicks off everything else. When the reactor has no
# more events to process, it exits.
r.run()
