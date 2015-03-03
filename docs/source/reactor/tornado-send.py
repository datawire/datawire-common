#!/usr/bin/python

import sys, tornado.ioloop
from tornado_app import TornadoApp
from proton import Message
from proton.handlers import CHandshaker

class Send:

    def __init__(self, host, message):
        self.host = host
        self.message = message
        # Use the handlers property to add some default handshaking
        # behaviour.
        self.handlers = [CHandshaker()]

    def on_connection_init(self, event):
        conn = event.connection
        conn.hostname = self.host

        # Every session or link could have their own handler(s) if we
        # wanted simply by setting the "handler" slot on the
        # given session or link.
        ssn = conn.session()

        # If a link doesn't have an event handler, the events go to
        # its parent session. If the session doesn't have a handler
        # the events go to its parent connection. If the connection
        # doesn't have a handler, the events go to the reactor.
        snd = ssn.sender("sender")
        conn.open()
        ssn.open()
        snd.open()

    def on_link_flow(self, event):
        snd = event.sender
        if snd.credit > 0:
            dlv = snd.send(self.message)
            dlv.settle()
            snd.close()
            snd.session.close()
            snd.connection.close()

class Program:

    def __init__(self, hostname, content):
        self.hostname = hostname
        self.content = content

    def on_reactor_init(self, event):
        # You can use the connection method to create AMQP connections.

        # This connection's handler is the Send object. All the events
        # for this connection will go to the Send object instead of
        # going to the reactor. If you were to omit the Send object,
        # all the events would go to the reactor.
        event.reactor.connection(Send(self.hostname, Message(self.content)))

args = sys.argv[1:]
hostname = args.pop() if args else "localhost"
content = args.pop() if args else "Hello World!"

TornadoApp(Program(hostname, content))
tornado.ioloop.IOLoop.instance().start()
