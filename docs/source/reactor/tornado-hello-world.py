#!/usr/bin/python

import tornado.ioloop
from tornado_app import TornadoApp

class Program:

    def on_reactor_init(self, event):
        print "Hello, World!"

# The TornadoApp integrates a Reactor into tornado's ioloop.
TornadoApp(Program())

# Now the tornado main loop will behave like the reactor's main loop.
tornado.ioloop.IOLoop.instance().start()
