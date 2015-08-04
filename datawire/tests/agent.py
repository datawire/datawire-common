# Copyright 2015 datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from proton import Message
from proton.reactor import Reactor
from datawire import Agent, Receiver

from common import *

class AgentTest:

    def __init__(self):
        class FakeTether:
            def __init__(self):
                self.address = None
                self.agent = None
                self.agent_type = None
        self.agent = Agent(FakeTether(), self)
        self.server = Server(self.agent)
        self.reactor = Reactor(self.server)
        self.samples = 0

    def teardown(self):
        self.server.acceptor.close()

    def sample(self, stats):
        stats["samples"] = self.samples
        self.samples += 1

    def testAgent(self, count=1, frequency=10):
        self.server.max_connections = 1
        self.agent.sampler.frequency = frequency
        class Counter:
            def __init__(self):
                self.received = 0
            def on_message(self, event):
                assert event.message.body["samples"] == self.received, (event.message.body, self.received)
                self.received += 1
                if self.received == count:
                    rcv.stop(event.reactor)
        rcv = Receiver("//localhost:%s" % PORT, Processor(Counter()))
        rcv.start(self.reactor)
        self.reactor.run()

    def testAgent10M100F(self):
        self.testAgent(10, 100)
