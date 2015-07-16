# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from unittest import TestCase
from proton import Message
from proton.reactor import Reactor
from datawire import Agent, Receiver

from common import *

class AgentTest(TestCase):

    def setUp(self):
        class FakeTether:
            def __init__(self):
                self.address = None
                self.agent = None
                self.agent_type = None
        self.agent = Agent(FakeTether(), self)
        self.server = Server(self.agent)
        self.reactor = Reactor(self.server)
        self.samples = 0

    def tearDown(self):
        if self.server.acceptor:
            self.server.acceptor.close()

    def sample(self, stats):
        stats["samples"] = self.samples
        self.samples += 1

    def testAgent(self, count=1, frequency=10):
        self.server.max_connections = 1
        self.agent.sampler.frequency = frequency
        class Counter(Timeout):
            def __init__(self):
                self.received = 0
            def on_message(self, event):
                assert event.message.body["samples"] == self.received, (event.message.body, self.received)
                self.received += 1
                if self.received == count:
                    rcv.stop(event.reactor)
                    self.cancel()
            def on_timer_task(self, event):
              rcv.stop(event.reactor)
        
        counter = Counter()
        rcv = Receiver("//localhost:%s" % PORT, Processor(counter))
        rcv.start(self.reactor)
        counter.set_timeout(self.reactor, 2)
        self.reactor.run()
        assert counter.cancelled, "Sampling timed out"

    def testAgent10M100F(self):
        self.testAgent(10, 100)
