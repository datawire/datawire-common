# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from proton import Message
from proton.reactor import Reactor
from datawire import Agent, Receiver

from common import *

class AgentTest:

    def __init__(self):
        self.agent = Agent(self)
        self.server = Server(self.agent)
        self.reactor = Reactor(self.server)
        self.samples = 0

    def on_sample(self, event):
        event.link.send(Message("sample-%s" % self.samples))
        self.samples += 1

    def testAgent(self, count=1, frequency=10):
        self.server.max_connections = 1
        self.agent.sampler.frequency = frequency
        class Counter:
            def __init__(self):
                self.received = 0
            def on_message(self, event):
                assert event.message.body == "sample-%s" % self.received, (event.message.body, self.received)
                self.received += 1
                if self.received == count:
                    rcv.stop(event.reactor)
        rcv = Receiver("//localhost:%s" % PORT, Processor(Counter()))
        rcv.start(self.reactor)
        self.reactor.run()

    def testAgent10M100F(self):
        self.testAgent(10, 100)
