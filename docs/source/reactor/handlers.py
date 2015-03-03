#!/usr/bin/python

import time
from proton.reactor import Reactor

class World:

    def on_reactor_init(self, event):
        print "World!"

class Goodbye:

    def on_reactor_final(self, event):
        print "Goodbye, World!"

class Hello:

    def __init__(self):
        self.handlers = [World(), Goodbye()]

    # The parent handler always receives the event first.
    def on_reactor_init(self, event):
        print "Hello",

r = Reactor(Hello())
r.run()
