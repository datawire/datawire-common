Install
=======

Datawire installs on Linux, and requires a basic toolchain to
install. On a yum-based system, install the following packages::

  yum install gcc libuuid-devel openssl-devel swig python-devel unzip tar make patch cmake
 
On an apt-based system, update your system with ``apt-get``, and then
install the following packages::

  apt-get update
  apt-get install curl gcc uuid-dev libssl-dev swig python-dev unzip make patch cmake

Once you've satisfied the necessary dependencies, install the latest
version of Datawire:

  curl http://www.datawire.io/install.sh | /bin/sh

This will install into the `datawire-XX` directory all Datawire
components, including the microserver, command line interface, service
locator, and example microservices. This also creates symlinks in the
user's local ``site-packages`` directory to the Datawire libraries, so
you can write code using the Datawire APIs without hacking your
PYTHONPATH.

The rest of this tutorial will walk you through Datawire. Because
we'll be sending and receiving messages, it will be easiest if you can
keep three different terminal windows open: one for the sender, one
for the receiver, and one for status commands. This tutorial will
refer to the sender window, receiver window, and command window to
help you keep track.

Sending / Receiving Messages
============================

We'll start by sending messages between a sender and receiver. In your
first terminal window, start up the receiver::

  examples/recv --physical //localhost:5678 //localhost/recv

This binds the receiver to the physical port ``localhost:5678``, and
registers a logical address of ``localhost/recv``. Let's take a quick
peek at the code:

.. literalinclude:: ../../../examples/recv
   :language: python

The receiver is implemented as a service, which is just an ordinary
process that binds to a local port and accepts incoming AMQP
connections.

Datawire uses Apache Qpid Proton (see http://qpid.apache.org/proton)
to handle incoming messages. Proton provides a high performance,
asynchronous event dispatcher called the ``Reactor`` which natively
processes AMQP 1.0 messages. In the ``on_reactor_init`` function, we
initialize the ``Reactor``:

.. literalinclude:: ../../../examples/recv
   :language: python
   :pyobject: Service.on_reactor_init

Finally, we implement the ``on_message`` function which is called by
the ``Reactor`` when a new message arrives. In this example, we just
print the message out.

.. literalinclude:: ../../../examples/recv
   :language: python
   :pyobject: Service.on_message

We can now send messages directly to the physical address. In a
different terminal window, type::

  examples/send //localhost:5678

You'll see a "Hello, World" message appear on STDOUT. This creates a
direct peer-to-peer connection for sending a message. You can also try
to send a message to the logical address::

  examples/send //localhost/recv

Which will fail, because the send program does not know about the
logical address. We're going to show how you can use logical
addresses, next.

.. note:: Messages are sent by default on port 5672 (the IANA assigned
	  port for AMQP). Make sure you don't have a firewall
	  filtering port 5672, or none of these examples will work.

The Service Locator
===================

Although clients can connect directly to a service if they know its
physical address, as shown above, it's usually not a good idea to tie
a service to a single physical address. This address might change due
to hardware or network failures, or you may want to deploy additional
instances of a service for load balancing purposes.

The Datawire `service locator` maps physical addresses to logical
addresses. To maximize scalability, performance, and reliability, the
service locator does not directly route or process messages. Instead,
it redirects AMQP links. Thus, messages still flow directly from
senders to receivers, and the service locator simply provides routing
directions. This is distinct from a traditional message broker
architecture, where the broker provides centralized service locator
and message processing capabilities. In the command window, start
the service locator by invoking it from the command line::

  directory &

Now, we can use ``dw``, the command-line interface to Datawire, to add
a route into the locator::

  dw route add //localhost:5678 //localhost/recv

Wcan rerun the previous send command to a logical address that failed::

  examples/send //localhost/recv

You'll see the Hello, World message now appears in the receiver.

Connecting Services to Datawire
===============================

There are several ways to connect services to Datawire. In the example
above, recv uses a ``tether`` to connect to Datawire. A tether is the
easiest way to connect services to Datawire. The tether provides live route
information and heartbeat data to the service locator. If a heartbeat
dies, the service locator stops routing messages to the service until
the heartbeat is restored.

The recv service we've been using does not use a tether. Let's switch
to the printer service, which is identical to the recv service, except
that it uses a tether. In the receiver window, terminate the receiver
(Ctrl-C), and start the printer service::

  examples/printer //localhost:5678 //localhost/printer

The tether automatically registers the logical and physical address,
which you can see by sending directly to the printer address::

  examples/send //localhost/printer

The printer service has automatically added a route; there is no need
to manually add a route. Code-wise, we create a tether in
``__init__``::

  .. literalinclude:: ../../../examples/printer
   :language: python
   :pyobject: Service.__init__

and then we start the tether in ``on_reactor_init``::

  .. literalinclude:: ../../../examples/printer
   :language: python
   :pyobject: Service.on_reactor_init

Let's now see the tether in action. In the command window, we'll
subscribe to the service locator routing table::

  dw route list -f

We're subscribing (``-f``, for follow) to the routing table message
stream. You'll see routing rules that map between the physical address
and logical address of the ``recv`` service. This view will update in
real-time.

In the receiver window, terminate the printer service. You'll see the
route disappear from the route list. Start the printer service again,
and you'll see the route reappear.

Similarly, if the locator dies, the routes will be regenerated when
the locator reappears.

Message Processing Pipelines
============================

So far, we've shown how you can asynchronously send and receive
messages, and how the service locator redirects messages from logical
addresses to physical addresses. We're now going to show how you can
build `message processing pipelines` where a message can be sent
through multiple services that process and transform the message.

We'll start by running a new microservice, ``upper``. ``upper`` simply
uppercases all the letters in a message::

  examples/upper --physical //localhost:5680 //localhost/transform //localhost/recv &
  
This configures the upper service to receive messages at the
``/localhost/transform`` address, and forward its processed messages to
``//localhost/receiver``. (We can run it as a background process
because this example doesn't output to STDOUT.)

Now, we can send a message to the upper service::

  examples/send //localhost/transform

We'll see that the original receiver receives a capitalized
message. We've just created a simple message processing pipeline. You
can also bypass the pipeine by sending a message directly to
``//localhost/receiver``. In this way, we've set up a processing
pipeline that is transparent to the receiver.

Load Balancing
==============

In most scenarios, you'll actually want to set up a processing
pipeline that's transparent to the `sender`, not the receiver. We'll
show how this can be done by creating a load balancer in front of the
receiver. 

Let's now create a "lower" microservice by copying the upper
microservice, and changing the ``on_message`` event handler::

  def on_message(self, event):
      if hasattr(event.message.body, "lower"):
          event.message.body = event.message.body.lower()
      self.stream.put(event.message)

Instead of just starting the new service on a different service
address, let's start it up on the same transform address::

  examples/lower -p //localhost:5681 //localhost/transform //localhost/receiver &

We now have two separate services, upper and lower, that are on the
same ``//localhost/transform`` address, and on different physical
addresses. Now, let's try sending a few more messages to the transform
address::

  examples/send //localhost/transform
  examples/send //localhost/transform
  examples/send //localhost/transform
  ...

You'll see that the original Hello, World message is randomly received
as all caps, or all lower case. This is because Datawire is
automatically load balancing between the two different services.

Dataflow
========

In Datawire, we use the term `dataflow` to refer to your messaging
topology. Load balancing is a type of dataflow. By thinking about the
dataflow of your system, you can easily identify how your system can
be broken into smaller microservices. Since you will probably want to
iterate on your dataflow over time, Datawire makes it easy to
reconfigure your dataflow, without changing any of your software
components. 

We're now going to walk through a more complex dataflow example to
give you a better sense of what Datawire can do.

Working with Datawire
=====================

The ``dw`` command line tool gives you a few different commands to
inspect and monitor Datawire settings. You've already seen the ``dw
route list -f`` command. If you want to just query the routing table,
just type::

  dw route list

You can also get a list of all local configuration settings with the
config list command::

  dw config list

All of these commands send and receive data as AMQP messages. Thus,
Datawire makes it easy to write a microservice that controls,
processes, or displays any of this data.

Receiving Messages
==================

So far, we've only discussed different ways to configure Datawire
microservices, but not how you actually write a microservice. Datawire
tries to make it as simple as possible for developers to write their
own microservices. Today, we include native support for Python and C,
with JavaScript and Ruby not too far behind.


Sending Messages
================

The code to send messages parallels the receiver code:

.. literalinclude:: ../../../examples/send
   :language: python

Instead of the ``on_message`` function, the message is initialized in
``on_reactor_init``:

.. literalinclude:: ../../../examples/send
   :language: python
   :pyobject: Client.on_reactor_init

**rafi, would you always encode sending in the init function?**

