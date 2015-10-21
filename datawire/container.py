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

from proton.handlers import CHandshaker
from .linker import Sender, Receiver

from .impl import dual_impl

@dual_impl
def ancestors(address):
    if address is None:
        yield address 
        return
    address = address.split("?", 1)[0]
    path = address.split("/")
    while path:
        addr = "/".join(path)
        yield addr
        if path[-1]:
            path[-1] = ""
        else:
            path.pop()

@dual_impl
class Container:

    def __init__(self, root=None):
        self.root = root
        self.nodes = {}
        self.links = []
        self.handlers = [CHandshaker()]

    def __setitem__(self, address, handler):
        self.nodes[address] = handler

    def __getitem__(self, address):
        for prefix in ancestors(address):
            if prefix in self.nodes:
                return self.nodes[prefix]
        return self.root

    def _link(self, type, local, remote, handlers, **kwargs):
        if not handlers:
            # XXX: why do we add node handler only when no handlers are specified
            node = self[local]
            if node: handlers = (node,)
        link = type(remote, *handlers, **kwargs)
        self.links.append(link)
        # XXX: links created after container.start() will not get started
        return link

    def sender(self, target, *handlers, **kwargs):
        # XXX: seems like a huge overlap with Linker.sender() 
        source = kwargs.get("source", None)
        return self._link(Sender, source, target, handlers, **kwargs)

    def receiver(self, source, *handlers, **kwargs):
        # XXX: ditto
        target = kwargs.get("target", None)
        return self._link(Receiver, target, source, handlers, **kwargs)

    def start(self, reactor):
        for l in self.links:
            l.start(reactor)

    def stop(self, reactor):
        for l in self.links:
            l.stop(reactor)

    def on_link_remote_open(self, event):
        link = event.link
        if link.is_sender:
            address = link.remote_source.address
        else:
            address = link.remote_target.address
        # XXX: isn't this dangerous to set handler unconditionally, doesn't this overwrite the handler for outgoing links?
        link.handler = self[address]
        if link.handler:
            event.dispatch(link.handler)

    def on_reactor_quiesced(self, event):
        event.dispatch(self.root)
        for h in self.nodes.values():
            event.dispatch(h)

    def on_transport_closed(self, event):
        event.connection.free()
