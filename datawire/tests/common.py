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

from proton import EventType, Message
from proton.handlers import CHandshaker
from datawire import Processor

class Source:

    def __init__(self, template="test-%s", start=0, limit=None, window=1024):
        self.template = template
        self.count = start
        self.limit = limit
        self.window = window
        self.message = Message()
        self.handlers = [CHandshaker()]

    def on_link_flow(self, event):
        if event.sender:
            self.pump(event.sender)

    def pump(self, snd):
        while self.count != self.limit and snd.credit > 0 and snd.queued < self.window:
            self.message.body = self.template % self.count
            dlv = snd.send(self.message)
            dlv.settle()
            self.count += 1

class Sink(Processor):

    def __init__(self):
        Processor.__init__(self)
        self.messages = []

    def on_message(self, event):
        msg = event.message
        self.messages.append(msg.body)

PORT = 5678

OPENED = EventType("opened")
CLOSED = EventType("closed")

class Closer:

    def __init__(self, delegate, closer):
        self.delegate = delegate
        self.closer = closer

    def on_connection_bound(self, event):
        event.dispatch(self.delegate)
        event.dispatch(self.closer, OPENED)

    def on_connection_unbound(self, event):
        event.dispatch(self.delegate)
        event.dispatch(self.closer, CLOSED)

    def on_unhandled(self, name, event):
        event.dispatch(self.delegate)

class Server:

    def __init__(self, delegate):
        self.delegate = delegate
        self.acceptor = None
        self.opened = 0
        self.closed = 0
        self.max_connections = None

    def on_opened(self, event):
        self.opened += 1

    def on_closed(self, event):
        self.closed += 1
        if self.max_connections is not None and self.closed >= self.max_connections:
            self.acceptor.close()

    def on_reactor_init(self, event):
        self.acceptor = event.reactor.acceptor("localhost", PORT, Closer(self.delegate, self))

