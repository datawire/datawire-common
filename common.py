"""
.. module:: common
   :platform: Unix
   :synopsis: Provides the classes which act as the backbone of datawire

The common module which acts as the backbone for datawire.io

.. moduleauthor:: Rafael Schloming, Richard Li

"""
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
    """This class provides a logger which writes to stdout if trace is enabled.
    
    :param trace: whether or not the log will be printed to stdout.  Defaults to False
    :type trace: boolean
    
    """
    
    def __init__(self, trace=False):
        self.trace = trace
    
    def log(self, msg, *args):
        """Writes msg to the log formatted with \*args (if provided).
        
        The log is written to standard out if trace is enabled.
        
        :param msg: the message to be written to standard out, or a format string to be formatted with \*args
        :param \*args: additional arguments used to format the format string, msg
        :type msg: a string
        :type \*args: any types compatabile with the format string, msg
        :returns: None
        
        :Example:
        
        >>> log = Logger(trace=True)
        >>> log.log("Hello world!")
        Hello world!
        >>> name = "John"
        >>> log.log("Hello %s", name)
        Hello John
        """
        if self.trace:
            sys.stderr.write(("%s\n" % msg) % args)
            sys.stderr.flush()
class Row:
    """An iterable unordered collection of links.  Starts empty.
    
    .. seealso:: `proton.Link <http://qpid.apache.org/releases/qpid-proton-0.8/protocol-engine/python/api/proton.Link-class.html>`_
    
    :Example:
    
    >>> lnk = event.link
    >>> row = Row()
    >>> len(row)
    0
    >>> bool(row)
    False
    >>> row.add(lnk)
    >>> len(row)
    1
    >>> bool(row)
    True
    >>> row.choose() is lnk
    True
    >>> row.discard(lnk)
    >>> len(row)
    0
    >>> bool(row)
    False
    >>> row.choose() is None
    True
    
    """

    def __init__(self):
        self.links = set()

    def add(self, link):
        """adds a link to the collection if the link is not already in the collection (no duplicates)

        :param link: the link to add to the collection
        :type link: proton.Link
        """
        self.links.add(link)

    def discard(self, link):
        """removes a given link from the collection if present, and takes no action if link not present in collection

        :param link: the link to remove
        :type link: proton.Link
        """
        self.links.discard(link)

    def choose(self):
        """ selects and returns a pseudo-random link from the collection or None if the collection is empty

        :returns: a random link from the collection or None if collection is empty
        :rtype: proton.Link or None
        """
        if self.links:
            return random.choice(list(self.links))
        else:
            return None

    def __len__(self):
        return len(self.links)

    def __iter__(self):
        return iter(self.links)

    def __nonzero__(self):
        return bool(self.links)


class Router:
    """Provides a routing map from address string to common.Row's of incoming and outgoing links.  Initialized empty.
    
    .. note:: TODO:  use common.Address rather than address string for keys

    The manual way to use the Router would be as follows:

    :Example:

    >>> router = Router()
    >>> len(router.incoming("//localhost"))
    0
    >>> # Later, after a connection is made to //localhost and we have rcv, a receiver proton.Link
    >>> router.add(rcv)
    >>> router.address(rcv)
    '//localhost'
    >>> router.incoming("//localhost").choose() is rcv
    True
    >>> router.outgoing("//localhost").choose() is None
    True
    >>> router.remove(rcv)
    >>> router.incoming("//localhost").choose() is rcv
    False

    Rather than manually adding and removing links in the receiver, the better paradigm would be
    to add the Router as a handler to the microservice, so its on_link_local_open,
    on_link_local_close, and on_link_local_final event handlers are triggered, adding and removing 
    the appropriate links when dispatched by the reactor.

    :Example:

    >>> # ... in a microservice init function...
    >>> self.router = Router()
    >>> self.handlers = [self.router]
    >>> # ... elsewhere, when attempting to access a link...
    >>> snd = self.router.outgoing("//localhost").choose()
    
    This paradigm is used in the service.Service class, which is the base class for microservices

    """
    # TODO:  use common.Address rather than address string for keys

    EMPTY = Row()

    def __init__(self):
        self._outgoing = {}
        self._incoming = {}

    def incoming(self, address):
        """
        Retrieves a row of receiver links from the given address,
        or an empty row if no receiver links from the given address exist.

        :param address: the address of the remote
        :type address: string
        :returns: a row of receiver links (which may be empty)
        :rtype: common.Row
        
        """
        return self._incoming.get(address, self.EMPTY)

    def outgoing(self, address):
        """
        Retrieves a row of sender links to the given address,
        or an empty row if no sender links to the given address exist.

        :param address: the address of the remote
        :type address: string
        :returns: a row of sender links (which may be empty)
        :rtype: common.Row
        
        """
        return self._outgoing.get(address, self.EMPTY)

    def address(self, link):
        """
        Retrieves the remote address of a given link.

        :param link: the link whose address will be retrieved
        :type link: proton.Link
        :returns: the address of the remote end of the link
        :rtype: string
        
        """
        if link.is_sender:
            return link.target.address or link.source.address
        else:
            return link.target.address

    def _table(self, link):
        """
        Gets the appropriate map (of incoming or outgoing connections)
        depending on whether the given link is a sender or receiver.

        :param link: the link whose type will be used to determine which
                     map should be returned
        :type link: proton.Link
        :returns: the dictionary of either outgoing or incoming connections
        :rtype: dictionary of string->Row
        """
        if link.is_sender:
            return self._outgoing
        else:
            return self._incoming

    def add(self, link):
        """
        adds link to the router

        :param link: the link to add
        :type link: proton.Link
        """
        address = self.address(link)
        table = self._table(link)
        row = table.get(address)
        if row is None:
            row = Row()
            table[address] = row
        row.add(link)

    def remove(self, link):
        """
        removes link from the router if present

        :param link: the link to remove from the router (if present)
        :type link: proton.Link
        """
        address = self.address(link)
        table = self._table(link)
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
    """
    .. deprecated:: 0.0.1
    """

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
    """A handler for microservices which manages deliveries for incoming connections,
    parsing them into complete messages and then dispatching a delegate's on_message
    handler when the delivery is complete.

    :param delegate: a class with an on_message method which will be dispatched with
                     two arguments:  the receiver link over which the message was delivered
                     and the decoded message.
    :type delegate: subclass of Service

    :Example:

    >>> # in init function for microservice (implemented automatically in Service)...
    >>> self.handlers = [MessageDecoder(self)]
    >>> 
    >>> # As a method in the microservice class:
    >>> def on_message(self, rcv, msg):
    ...     # Handle the message here
    ...
    >>>

    """

    def __init__(self, delegate):
        self.__delegate = delegate
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
    """Represents a remote address with an optional UID specified in the form:

    /<UID>::<REMOTE ADDRESS>

    <REMOTE ADDRESS> typically begins with "//"

    :param st: the string representing the address in the format specified above
    :type st: string

    :Example:

    >>> address = Address("/me:://test.datawire.io:5680/example")
    >>> address.local
    '/me'
    >>> address.remote
    '//test.datawire.io:5680/example'
    >>> address.host
    'test.datawire.io:5680'
    >>> address.path
    'example'
    >>> # Given a link, lnk, whose address needs to be configured to be address:
    >>> address.configure(lnk)

    """

    def __init__(self, st):
        if st and "::" in st:
            self.local, self.remote = st.split("::", 1)
        else:
            self.local = None
            self.remote = st

    @property
    def host(self):
        """
        The host and port of the address

        :rtype: string
        """
        if self.remote is None: return None
        if self.remote.startswith("//"):
            return self.remote[2:].split("/", 1)[0]
        else:
            return None

    @property
    def path(self):
        """
        The path of the address with no leading "/"

        :rtype: string
        """
        if self.remote is None: return None
        parts = self.remote[2:].split("/", 1)
        if len(parts) == 2:
            return parts[1]
        else:
            return ""

    def configure(self, obj):
        """
        Configures a link to point at the address.

        :param obj: the link
        :type obj: proton.Link
        
        """
        if isinstance(obj, Connection):
            conn = obj
            link = None
            # TODO:  This will cause a None type exception, which means
            # configure is probably only used to configure links now.
            # This cruft should be removed
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
    """
    Checks the link to see if it was closed due to a redirection and, if it was, returns
    the address to which the link was redirected.  If not closed due to redirection,
    returns None.

    :param link: the link which may or may not have been redirected and closed
    :type link: proton.Link
    :returns: the address to which the link was redirected (if redirected) or else None
    :rtype: common.Address or None
    
    """
    if link.remote_condition and link.remote_condition.name == "amqp:link:redirect":
        info = link.remote_condition.info
        host = info["network-host"]
        port = info["port"]
        return Address("//%s:%s" % (host, port))
    else:
        return None


class SendQueue:
    """
    A send queue is tasked with sending messages to a specific address specified at initialization.

    It must be connected either by dispatching the on_reactor_init event handler or by calling the 
    connect method directly.

    Queued messages will be held in the queue until they are able to be sent.

    The SendQueue will automatically attempt to reconnect on a 1 second interval if the link is
    closed.

    :param address: the address to which the send queue will send messages
    :type address: string
    
    :Example:
    
    >>> # Given an INITIALIZED instance of proton.reactors.Reactor, reactor:
    >>> sq = SendQueue("//localhost")
    >>> msg = Message()
    >>> msg.body = "Example Message"
    >>> # declare other properties of msg...
    >>> sq.put(msg)
    >>> # msg is on the queue to be sent to the server
    
    """

    def __init__(self, address):
        self.address = Address(address)
        self.messages = []
        self.sent = 0
        self.closed = False

    def on_reactor_init(self, event):
        """
        To be dispatched when the reactor is initialized.

        It starts the connection automatically.

        In a parent microservice's on_init_function, the send queue's on_reactor_init function
        can be dispatched using the following:

        :Example:

        >>> # In parent microservice's on_reactor_init function
        >>> event.dispatch(self.send_queue)
        
        """
        self.connect(event.reactor)

    def connect(self, reactor, network=None):
        """Connects the send queue manually given an initialized reactor

        :param reactor: the INITIALIZED reactor
        :param network: internally used to change the connection address in
                        case of redirect.  Should typically leave as default:  None
        :type reactor:  proton.reactors.Reactor
        :type network:  string or None

        :Example:

        >>> # the initialized Reactor is reactor
        >>> send_queue = SendQueue("//localhost")
        >>> send_queue.connect(reactor)
        
        """
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
        """Enqueues the message to be sent.

        :param message: the message to be sent
        :type message: proton.Message

        """
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
        """
        Closes the send queue and stops attempts to reconnect
        """
        self.closed = True
        if self.conn:
            self.conn.close()

# XXX: terrible name for this
class RecvQueue:
    """
    .. note:: TODO:  rename class

    Manages a connection with a receiver link to a remote address
    and handles redirects and reconnects (if connection is lost) on a
    1 second interval.
    
    When messages are received, the on_message handler of the specified
    delegate will be dispatched as specified in common.MessageDecoder.
    
    :param address: the address of the remote
    :param delegate: the delegate class (usually a subclass of service.Service)
                     which has an on_message event handler method which is
                     dispatched when a message is received
    :type address: string
    :type delegate: subclass of Service
    
    :Example:
    
    >>> # In init function of a service:
    >>> self.recv_queue = RecvQueue("//localhost", self)
    >>> # In on_reactor_init of the service:
    >>> event.dispatch(self.recv_queue) # starts the connection
    
    """

    def __init__(self, address, delegate):
        self.address = Address(address)
        self.delegate = delegate
        self.decoder = MessageDecoder(self.delegate)
        self.handlers = [FlowController(1024), self.decoder]
        self.closed = False

    def on_reactor_init(self, event):
        """
        To be dispatched when the reactor is initialized.
        
        It starts the connection automatically.
        
        In a parent microservice's on_init_function, the recv queue's on_reactor_init function
        can be dispatched using the following:
        
        :Example:
        
        >>> # In parent microservice's on_reactor_init function
        >>> event.dispatch(self.recv_queue)
        
        """
        event.dispatch(self.decoder)
        self.connect(event.reactor)

    def connect(self, reactor, network=None):
        """Connects the recv queue manually given an initialized reactor
        
        :param reactor: the INITIALIZED reactor
        :param network: internally used to change the connection address in
                        case of redirect.  Should typically leave as default:  None
        :type reactor:  proton.reactors.Reactor
        :type network:  string or None
        
        :Example:
        
        >>> # the initialized Reactor is reactor
        >>> recv_queue = RecvQueue("//localhost", self)
        >>> recv_queue.connect(reactor)
        
        """
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
        """
        Closes the recv queue and stops attempts to reconnect
        """
        self.closed = True
        if self.conn:
            self.conn.close()


class SendQueuePool:
    """
    Manages a collection of send queues keyed by address.
    
    Must be initialized when the reactor is initialized using:
    
    :Example:
    
    >>> # From within microservice's __init__ function:
    >>> self.send_queue_pool = SendQueuePool()
    >>> # From within microservice's on_reactor_init function:
    >>> event.dispatch(self.send_queue_pool)
    
    After initialized, the send queue pool can manage creating
    common.SendQueue's keyed by target address:
    
    :Example:
    
    >>> # Given a proton.Message, msg, one needs to send to //localhost...
    >>> self.send_queue_pool.to("//localhost").put(msg)

    """
    def __init__(self):
        self.pool = {}

    def on_reactor_init(self, event):
        self.dispatcher = event

    def to(self, addr):
        """
        Gets the common.SendQueue connected to the given address or creates one
        if it does not already exist.
        
        :param addr: the target address
        :type addr: string
        :returns: the send queue connected to addr
        :rtype: common.SendQueue
        
        """
        if addr in self.pool:
            return self.pool[addr]
        self.pool[addr] = SendQueue(addr)
        # self.pool[addr].on_start(self.drv)
        self.dispatcher.dispatch(self.pool[addr])
        return self.pool[addr]


def redirect_link(link, host="127.0.0.1", port=5672):
    """
    Given a connected link, redirects the link
    to the given host and port and closes
    the original link.
    
    :param link: the connected link which will be redirected
    :param host: the host to which the link will be redirected (default: "127.0.0.1")
    :param port: the port to which the link will be redirected (default: 5672)
    :type link: proton.Link
    :type host: string
    :type port: integer
    
    :Example:

    >>> # Given lnk, a proton.Link, which is connected
    >>> # Redirect lnk to //127.0.0.1:5680
    >>> redirect_link(lnk, host="127.0.0.1", port=5680)
    
    """
    link.condition = Condition("amqp:link:redirect", None,
       {symbol("network-host"): host,
        symbol("port"): str(port)})
    link.close()
