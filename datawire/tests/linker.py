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

from unittest import TestCase
from proton import Message
from proton.reactor import Reactor
from datawire import Linker, Processor, Receiver, Sampler, Sender, Stream

from .common import *

class SinkTest(TestCase):

    def setUp(self):
        self.sink = Sink()
        self.server = Server(self.sink)
        self.reactor = Reactor(self.server)
        
    def tearDown(self):
        pass

    def testSender(self, count=1):
        self.server.max_connections = 1
        snd = Sender("//localhost:%s" % PORT)
        self.reactor.handler.add(snd)
        snd.start(self.reactor)
        for i in range(count):
            snd.send("test-%s" % i)
        snd.close()
        self.reactor.run()
        assert len(self.sink.messages) == count
        for i in range(count):
            assert self.sink.messages[i] == "test-%s" % i, self.sink.messages[i]

    def testSender4K(self):
        self.testSender(4*1024)

    def testSampler(self, count=1, frequency=10):
        self.server.max_connections = 1
        oself = self
        class Gen(Timeout):
            def __init__(self):
                self.sent = 0

            def on_sample(self, event):
                event.link.send(Message("test-%s" % self.sent))
                self.sent += 1
                if self.sent >= count:
                    event.link.close()
                    self.cancel()
            def on_timer_task(self, event):
              snd.stop(event.reactor)
        gen = Gen();
        snd = Sender("//localhost:%s" % PORT, Sampler(gen, frequency))
        self.reactor.handler.add(snd)
        gen.set_timeout(self.reactor, 2)
        snd.start(self.reactor)
        self.reactor.run()
        assert gen.cancelled, "Sampling timed out"
        assert len(self.sink.messages) == count, len(self.sink.messages)
        for i in range(count):
            assert self.sink.messages[i] == "test-%s" % i

    def testSampler100M100F(self):
        self.testSampler(100, 100)

    def testLinker(self, address_count=1, message_count=1):
        self.server.max_connections = address_count
        linker = Linker()
        linker.start(self.reactor)
        for i in range(address_count):
            for j in range(message_count):
                snd = linker.sender("//localhost:%s/%s" % (PORT, i))
                assert len(linker.senders) == i + 1
                snd.send(dict(i=i, j=j))
        linker.close()
        self.reactor.run()

        by_addr = dict((i,[]) for i in range(address_count))
        for m in self.sink.messages:
          by_addr[m["i"]].append(m)
        for addr, msgs in by_addr.iteritems():
          self.assertSequenceEqual(msgs, list(sorted(msgs, key=lambda x:(x["i"],x["j"]))))
        self.assertEqual(len(self.sink.messages), address_count*message_count)

    def testLinker2A1M(self):
        self.testLinker(2, 1)

    def testLinker4A1M(self):
        self.testLinker(4, 1)

    def testLinker16A1M(self):
        self.testLinker(16, 1)

    def testLinker1A2M(self):
        self.testLinker(1, 2)

    def testLinker1A4M(self):
        self.testLinker(1, 4)

    def testLinker1A16M(self):
        self.testLinker(1, 16)

    def testLinker2A2M(self):
        self.testLinker(2, 2)

    def testLinker4A4M(self):
        self.testLinker(4, 4)

    def testLinker16A16M(self):
        self.testLinker(16, 16)


class SourceTest(TestCase):

    def setUp(self):
        self.source = Source("test-%s")
        self.server = Server(self.source)
        self.reactor = Reactor(self.server)
        
    def tearDown(self):
      pass

    def testReceiver(self, count=1):
        self.server.max_connections = 1
        self.source.limit = count

        oself = self

        class Counter:
            def __init__(self):
                self.received = 0
                self.receiver = None
                self.open_event = False

            def on_link_remote_open(self, event):
                self.open_event = True

            def on_message(self, event):
                assert event.message.body == oself.source.template % self.received
                self.received += 1
                if self.received == count:
                    self.receiver.stop(event.reactor)

        counter = Counter()
        rcv = Receiver("//localhost:%s" % PORT, Processor(counter))
        counter.receiver = rcv
        self.reactor.handler.add(rcv)
        rcv.start(self.reactor)
        self.reactor.run()
        assert counter.received == count
        assert counter.open_event

    def testReceiver150(self):
        self.testReceiver(150)

    # This doesn't seem to work for any value > 150! This is a proton
    # bug that needs to be isolated and pushed upstream. Enable and
    # run under valgrind for more details.
    def XXXtestReceiver151(self):
        self.testReceiver(151)
