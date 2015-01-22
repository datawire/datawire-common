#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import sys, re, traceback
from proton import *
from proton.reactors import Reactor
from proton.handlers import CHandshaker as Handshaker, \
    CFlowController as FlowController

del Driver, Connector, Listener, Handler

uid_pattern = re.compile('^/[A-Za-z0-9_-]*$')

class Logger(object):

    def log(self, msg, *args):
        if self.trace:
            sys.stderr.write(("%s\n" % msg) % args)
            sys.stderr.flush()
class Row:

    def __init__(self):
        self.links = set()

    def add(self, link):
        self.links.add(link)

    def discard(self, link):
        self.links.discard(link)

    def choose(self):
        if self.links:
            return random.choice(list(self.links))
        else:
            return None

    def __iter__(self):
        return iter(self.links)

    def __nonzero__(self):
        return bool(self.links)


class Router:

    EMPTY = Row()

    def __init__(self):
        self._outgoing = {}
        self._incoming = {}

    def incoming(self, address):
        return self._incoming.get(address, self.EMPTY)

    def outgoing(self, address):
        return self._outgoing.get(address, self.EMPTY)

    def address(self, link):
        if link.is_sender:
            # TODO:  Check to make sure priority swap was safe
            return link.target.address or link.source.address
        else:
            return link.target.address

    def table(self, link):
        if link.is_sender:
            return self._outgoing
        else:
            return self._incoming

    def add(self, link):
        address = self.address(link)
        table = self.table(link)
        row = table.get(address)
        if row is None:
            row = Row()
            table[address] = row
        row.add(link)

    def remove(self, link):
        address = self.address(link)
        table = self.table(link)
        row = table.get(address)
        if row is not None:
            row.discard(link)
            if not row:
                del table[address]

    def on_link_local_open(self, event):
        self.add(event.context)

    def on_link_local_close(self, event):
        self.remove(event.context)

    def on_link_final(self, event):
        self.remove(event.context)

class Pool:

    def __init__(self, driver, router=None):
        self.driver = driver
        self._connections = {}
        if router:
            self.outgoing_resolver = lambda address: router.outgoing(address).choose()
            self.incoming_resolver = lambda address: router.incoming(address).choose()
        else:
            self.outgoing_resolver = lambda address: None
            self.incoming_resolver = lambda address: None

    def resolve(self, remote, local, resolver, constructor):
        link = resolver(remote)
        if link is None:
            host = remote[2:].split("/", 1)[0]
            conn = self._connections.get(host)
            if conn is None:
                conn = self.driver.connection()
                conn.hostname = host
                conn.open()
                self._connections[host] = conn

            ssn = conn.session()
            ssn.open()
            link = constructor(ssn, remote, local)
            link.open()
        return link

    def on_transport_closed(self, event):
        transport =  event.context
        conn = transport.connection
        del self._connections[conn.hostname]

    def outgoing(self, target, source=None):
        return self.resolve(target, source, self.outgoing_resolver, self._new_outgoing)

    def incoming(self, source, target=None):
        return self.resolve(source, target, self.incoming_resolver, self._new_incoming)

    def _new_outgoing(self, ssn, remote, local):
        snd = ssn.sender("%s-%s" % (local, remote))
        snd.source.address = local
        snd.target.address = remote
        return snd

    def _new_incoming(self, ssn, remote, local):
        rcv = ssn.receiver("%s-%s" % (remote, local))
        rcv.source.address = remote
        rcv.target.address = local
        return rcv

class MessageDecoder:

    def __init__(self, delegate):
        self.__delegate = delegate

    def on_reactor_init(self, event):
        try:
            self.__delegate
        except AttributeError:
            self.__delegate = self
        self.__message = Message()

    def on_delivery(self, event):
        dlv = event.context
        if dlv.link.is_receiver and not dlv.partial:
            encoded = dlv.link.recv(dlv.pending)
            self.__message.decode(encoded)
            try:
                dispatch(self.__delegate, "on_message", dlv.link, self.__message)
                dlv.update(Delivery.ACCEPTED)
            except:
                dlv.update(Delivery.REJECTED)
                traceback.print_exc()
            dlv.settle()

class Address:

    def __init__(self, st):
        if st and "::" in st:
            self.local, self.remote = st.split("::", 1)
        else:
            self.local = None
            self.remote = st

    @property
    def host(self):
        if self.remote is None: return None
        if self.remote.startswith("//"):
            return self.remote[2:].split("/", 1)[0]
        else:
            return None

    @property
    def path(self):
        if self.remote is None: return None
        parts = self.remote[2:].split("/", 1)
        if len(parts) == 2:
            return parts[1]
        else:
            return ""

    def configure(self, obj):
        if isinstance(obj, Connection):
            conn = obj
            link = None
        else:
            link = obj
            conn = link.session.connection

        if not conn.hostname and self.host:
            conn.hostname = self.host

        if link.is_sender:
            local = link.source
            remote = link.target
        else:
            local = link.target
            remote = link.source

        if self.local:
            local.address = self.local
        if self.remote:
            remote.address = self.remote

    def __repr__(self):
        return "Address(%r)" % self.st

    def __str__(self):
        return self.remote

def redirect(link):
    if link.remote_condition and link.remote_condition.name == "amqp:link:redirect":
        info = link.remote_condition.info
        host = info["network-host"]
        port = info["port"]
        return Address("//%s:%s" % (host, port))
    else:
        return None

class SendQueuePool:

    def __init__(self):
        self.pool = {}

    def on_start(self, drv):
        self.drv = drv

    def on_reactor_init(self, event):
        self.dispatcher = event

    def to(self, addr):
        if addr in self.pool:
            return self.pool[addr]
        self.pool[addr] = SendQueue(addr)
        # self.pool[addr].on_start(self.drv)
        self.dispatcher.dispatch(self.pool[addr])
        return self.pool[addr]

class SendQueue:

    def __init__(self, address):
        self.address = Address(address)
        self.messages = []
        self.sent = 0
        self.closed = False

    def on_reactor_init(self, event):
        self.connect(event.reactor)

    def connect(self, reactor, network=None):
        if network is None:
            network = self.address
        self.conn = reactor.connection(self)
        self.conn.hostname = network.host
        ssn = self.conn.session()
        snd = ssn.sender(str(self.address))
        self.address.configure(snd)
        ssn.open()
        snd.open()
        self.conn.open()
        self.link = snd

    def on_link_remote_close(self, event):
        link = event.link
        network = redirect(event.link)
        event.connection.close()
        if network:
            self.connect(event.reactor, network)

    def put(self, message):
        self.messages.append(message.encode())
        if self.link:
            self.pump(self.link)

    def on_link_flow(self, event):
        link = event.context
        self.pump(link)

    def pump(self, link):
        while self.messages and link.credit > 0:
            dlv = link.delivery(str(self.sent))
            bytes = self.messages.pop(0)
            link.send(bytes)
            dlv.settle()
            self.sent += 1

    def on_transport_closed(self, event):
        conn = event.connection
        if self.conn != conn: return
        self.conn = None
        self.link = None
        if not self.closed:
            event.reactor.schedule(1, self)

    def on_timer_task(self, event):
        self.connect(event.reactor)

    def close(self):
        self.closed = True
        if self.conn:
            self.conn.close()

# XXX: terrible name for this
class RecvQueue:

    def __init__(self, address, delegate):
        self.address = Address(address)
        self.delegate = delegate
        self.decoder = MessageDecoder(self.delegate)
        self.handlers = [FlowController(1024), self.decoder]
        self.closed = False

    def on_reactor_init(self, event):
        event.dispatch(self.decoder)
        self.connect(event.reactor)

    def connect(self, reactor, network=None):
        if network is None:
            network = self.address
        self.conn = reactor.connection(self)
        self.conn.hostname = network.host
        ssn = self.conn.session()
        rcv = ssn.receiver(str(self.address))
        self.address.configure(rcv)
        ssn.open()
        rcv.open()
        self.conn.open()

    def on_link_remote_close(self, event):
        link = event.link
        network = redirect(event.link)
        event.connection.close()
        if network:
            self.connect(event.reactor, network)

    def on_transport_closed(self, event):
        conn = event.connection
        if self.conn != conn: return
        self.conn = None
        if not self.closed:
            event.reactor.schedule(1, self)

    def on_timer_task(self, event):
        self.connect(event.reactor)

    def close(self):
        self.closed = True
        if self.conn:
            self.conn.close()

def redirect_link(link, host="127.0.0.1", port="5672"):
    link.condition = Condition("amqp:link:redirect", None,
       {symbol("network-host"): host,
        symbol("port"): port})
    link.close()
