#!/usr/bin/python

import time
from proton.reactor import Reactor

class Hello:

    def on_reactor_init(self, event):
        print "Hello, World!"

class Goodbye:

    def on_reactor_final(self, event):
        print "Goodbye, World!"

class Program:

    def __init__(self, *delegates):
        self.delegates = delegates

    def on_unhandled(self, name, event):
        for d in self.delegates:
            event.dispatch(d)

r = Reactor(Program(Hello(), Goodbye()))
r.run()
