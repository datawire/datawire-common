.. _dw_tutorial:

Tutorial
########

This tutorial will walk you through the install and configuration of
Datawire, as well as some simple code and usage scenarios.

Install
=======

Datawire installs on Linux, and requires a basic toolchain to
install. On a yum-based system, install the following packages::

  yum install gcc libuuid-devel openssl-devel swig python-devel unzip tar make patch cmake wget
 
On an apt-based system, update your system with ``apt-get``, and then
install the following packages::

  apt-get update
  apt-get install wget gcc uuid-dev libssl-dev swig python-dev unzip make patch cmake

Once you've satisfied the necessary dependencies, install the latest
version of Datawire::

  wget -O - https://www.datawire.io/install.sh | /bin/sh

This will install into the datawire-|version| directory all Datawire
components, including the microserver, command line interface,
directory, and example microservices. This also creates symlinks in
the user's local ``site-packages`` directory to the Datawire
libraries, so you can write code using the Datawire APIs without
editing your PYTHONPATH.

The install script also generates the ``dw-config.sh`` file, which
will set your environment variables correctly. Use the ``source``
command to run this file:

.. parsed-literal::

  source datawire-|version|/dw-config.sh

The rest of this tutorial will walk you through Datawire. Because
we'll be sending and receiving messages, it will be easiest if you can
keep three different terminal windows open: one for the sender, one
for the receiver, and one for status commands. This tutorial will
occasionally refer to the sender window, receiver window, and command
window to help you keep track.

Sending / Receiving Messages
============================

We'll start by sending messages between a sender and receiver. In your
first terminal window, start up the receiver:

.. parsed-literal::

  cd datawire-|version|/
  examples/recv --host localhost --port 5678

This binds the receiver to ``localhost:5678``. Let's take a quick
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
direct peer-to-peer connection for sending a message. The bulk of the
work for ``send`` is again done in ``on_reactor_init``:

.. literalinclude:: ../../../examples/send
   :language: python
   :pyobject: Client.on_reactor_init

.. note:: This tutorial uses several different ports, beginning with
          port 5672 (the IANA assigned port for AMQP), and going
          up 5684. Make sure you don't filter ports 5672 through 5684,
          or these examples will not work.

Directory
=========

Although clients can connect directly to a service if they know its
physical address, as shown above, it's usually not a good idea to tie
a service to a single physical address. This address might change due
to hardware or network failures, or you may want to deploy additional
instances of a service for load balancing purposes.

The Datawire `directory` maps physical addresses to logical
addresses. To maximize scalability, performance, and reliability, the
directory does not directly route or process messages. Instead,
it redirects AMQP links (unidirectional message flow). Thus, messages
still flow directly from senders to receivers, and the directory
simply provides routing directions. This is distinct from a
traditional message broker architecture, where the broker provides
centralized directory and message processing capabilities. In
the command window, start the directory by invoking it from the
command line::

  directory &

Now, we can use ``dw``, the command-line interface to Datawire, to add
a route into the directory::

  dw route add //localhost/recv //localhost:5678

You can verify that the route has been added with the ``route list``
command::

  dw route list

Now, we can send to a logical address, instead of just the physical
address. Let's create a new window in your terminal, the sender
window, and type::

  examples/send //localhost/recv

You'll see the Hello, World message now appears in the receiver. In
the sender, you'll see that the message is redirected by the
directory. By introducing a layer of indirection, you can change the
physical address of the receiver, without requiring any change in the
sender.

Connecting Services to Datawire
===============================

There are several ways to connect services to Datawire. In the above
example, we manually added a route using the command line. For
developers, the easiest way to connect to Datawire is to use a
`tether`. The tether provides live route information and heartbeat
data to the directory. If a heartbeat dies, the directory
stops routing messages to the service until the heartbeat is restored.

The recv service we've been using does not use a tether. Let's switch
to the printer service, which is identical to the recv service, except
that it uses a tether. In the receiver window, terminate the receiver
(Ctrl-C), and start the printer service::

  examples/printer --port 5678 //localhost/printer

The tether automatically registers the logical and physical address,
which you can see by sending directly to the printer address::

  examples/send //localhost/printer

The printer service has automatically added a route; there is no need
to manually add a route. Code-wise, we create a tether in
``__init__``:

.. literalinclude:: ../../../examples/printer
   :language: python
   :pyobject: Printer.__init__

and then we start the tether in ``on_reactor_init``:

.. literalinclude:: ../../../examples/printer
   :language: python
   :pyobject: Printer.on_reactor_init

Let's now see the tether in action. In the command window, we'll
subscribe to the directory routing table::

  dw route list -f

We're subscribing (``-f``, for follow) to the routing table message
stream. You'll see routing rules that map between the physical address
and logical address of the ``printer`` service. This view will update in
real-time.

In the receiver window, terminate the ``printer`` service. You'll see
the route disappear from the route list. Start the ``printer`` service
again, and you'll see the route reappear.

Similarly, if the directory dies, the routes will be regenerated when
the directory reappears.

Message Processing Pipelines
============================

So far, we've shown how you can asynchronously send and receive
messages, and how the directory redirects messages from logical
addresses to physical addresses. We're now going to show how you can
build `message processing pipelines` where a message can be sent
through multiple services that process and transform the message.

We'll start by running a new microservice, ``upper``. ``upper`` simply
uppercases all the letters in a message::

  examples/upper --port 5680 //localhost/transform //localhost/printer &

This configures the upper service to receive messages at the
``/localhost/transform`` address, and forward its processed messages to
``//localhost/printer``. (We can run it as a background process
because this example doesn't output to STDOUT.)

Now, we can send a message to ``upper`` in the sender window::

  examples/send //localhost/transform

We'll see that the original receiver receives a capitalized
message. We've just created a simple message processing pipeline. You
can also bypass the pipeine by sending a message directly to
``//localhost/printer``. In this way, we've set up a processing
pipeline that is transparent to the receiver.

Load Balancing
==============

In many scenarios, you'll actually want to set up a processing
pipeline that's transparent to the `sender`, not the receiver. We'll
show how this can be done by creating a load balancer in front of the
receiver.

Let's start by creating a "lower" microservice by copying the upper
microservice::

  cp examples/upper examples/lower

Then, edit the ``on_message`` event handler of ``lower`` to look like
this::

  def on_message(self, event):
      if hasattr(event.message.body, "lower"):
          event.message.body = event.message.body.lower()
      self.stream.put(event.message)

Let's start the ``lower`` service on the printer's address, along with
a new instance of the ``upper`` service::

  examples/lower --port 5681 //localhost/printer //localhost/display &
  examples/upper --port 5682 //localhost/printer //localhost/display &

Finally, let's terminate the current ``printer`` service (Ctrl-C), and
restart it on a new address::

  examples/printer --port 5678 //localhost/display

What we've just done is set up two services, ``lower`` and ``upper``,
that receive messages on ``//localhost/printer``, process them, and
pass on the results to ``//localhost/display``. The original
``printer`` microservice is now receiving messages on
``//localhost/display``. So, if we rerun our send command from above::

  examples/send //localhost/printer
  examples/send //localhost/printer
  examples/send //localhost/printer
  ...

You'll see that the original Hello, World message is randomly received
as all caps, or all lower case, as Datawire automatically load
balances between the ``upper`` and ``lower`` services. What's
important to note here is that we've just transparently added load
balancing without affecting the sender.

Fanout
======

In the load balancing example, the directory is changing the routes
dynamically between different microservices running on the same
address. Microservices themselves can also send messages on multiple
addresses. In this example, we'll start with setting up the fanout
example (you'll want to open a second receiver window, or run this in
the command window)::

  examples/printer --port 5683 //localhost/display2
  examples/fanout --port 5684 //localhost/fan //localhost/display //localhost/display2

Here, we're registering an address of ``localhost/fan`` and telling
``fanout`` to send any messages it receives to ``localhost/display``
and ``localhost/display2``. Now, run ``send`` again::

  examples/send //localhost/fan

and you'll see the message appear to both recipient addresses. Fanout
uses a ``Stream`` to simplify part of the code.

.. literalinclude:: ../../../examples/fanout
   :language: python
   :pyobject: Fanout
  
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

Using Multiple Hosts
====================

The localhost-only scenarios shown above can easily be modified to support
running microservices on multiple hosts. The key point to remember is that
any host running a microservice (printer, upper, lower, fanout) must also
run a directory. The non-service examples (send and bridge) do not need to
run on a host that is running a directory.

For the following example, consider a network with two hosts, sapphire and
may. Launch the directory and the display service on sapphire (in separate
terminals)::

  sapphire$ directory --host sapphire

  sapphire$ examples/printer //sapphire/display

Next, launch the directory and the upper service on may (again, in separate
terminals)::

  may$ directory --host may

  may$ examples/upper //may/upper //sapphire/display

Now we can use the multi-host message pipeline from any machine, with the
ultimate results being displayed by the display service on sapphire::

  anyHost$ examples/send //may/upper

The ``dw`` command line can also query remote directories. Pass in the
full directory address (including the ``//`` prefix and the
``directory`` suffix) to the ``-d`` option::

  may% dw -d //sapphire/directory route list
  
Network Bindings
================

In some environments, a microservice may need to bind to one IP
address and port, while remote processes must connect to a different
IP address and port to reach the microservice. Datawire supports these
scenarios by enabling you to set separate ``bind`` and ``announce``
addresses. By default, Datawire assumes that you want to set the
``bind`` address, and sets the ``announce`` address to be the
same. If you wish to set them differently, you can.

For the directory::

  directory -n bind_host -p bind_port -a //external_host

The example microservices also support this, e.g.,::

  examples/printer -n bind_host -p bind_port --ann-host external_host --ann-port external_port -d //external_host/directory //external_host/display

Bug Reporting and Known Issues
==============================

This is the |version| release. While our underlying libraries have
been used in numerous production scenarios, the full integrated
Datawire infrastructure has not. We expect that as more users use
Datawire, more bugs will be identified.

If you run into issues, please contact us at
support@datawire.io. Beside a bug report and reproducer (if
available), we may also request a debug trace. To get a debug trace,
type::

  export PN_TRACE_FRM=1

and rerun the commands. To turn off tracing, set ``PN_TRACE_FRM=0``.  

Next Steps
==========

Congratulations on making your way through the Datawire tutorial!
You've seen how to connect microservices in a variety of ways, using a
few different dataflows. Here are some things to try next:

1. Read the :ref:`reactor_tutorial`, which covers the difference types
   of events that can be used in a microservice.
2. Try modifying and running the examples in ``examples/``, including
   ``bridge``, which we haven't covered in this tutorial.
3. Try using Datawire in some of your microservices.
4. Send feedback about your use cases to support@datawire.io.
