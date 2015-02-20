Install
=======

Datawire installs on Linux, and requires a basic toolchain to
install. On a yum-based systems, install the following packages::

  yum install gcc libuuid-devel openssl-devel swig python-devel unzip tar make patch cmake
 
On an apt-based system, update your system and then install the
following packages::

  apt-get update
  apt-get install curl gcc uuid-dev libssl-dev swig python-dev unzip make patch cmake

Then, install the latest version of Datawire:

  curl http://www.datawire.io/install.sh | /bin/sh

This will install into the `datawire-XX` directory all Datawire
components, including the microserver, command line interface,
directory, and example microservices. This also creates symlinks in
the user's local ``site-packages`` directory to the Datawire
libraries, so you can write code using the Datawire APIs without
hacking your PYTHONPATH.

Now, start the directory service locally::

  bin/directory &

Connecting Microservices
========================

This example will show how Datawire can be used to connect two
different microservices. All of these examples assume that the
datawire-xx/bin directory is in your path. Because we'll be sending
and receiving messages, you'll want to keep a few different terminal
windows handy and open.

To start, we'll use the command line client to display what routes are
present in the directory::

  dw route list -f

This -f ("follow") argument subscribes to messages from the directory on the
addition/deletion of new routes.

Now, let's set up a receiver for the messages::

  examples/recv //localhost/receiver

This starts a program that listens for messages at the address
``//localhost/foo``. Note that this is a *logical* address, not a
physical one. If you go over to the route list window, you'll
see a route has appeared. (And if you stop the recv process by typing
Ctrl-C, you'll see the route disappears. Start the recv process again
if you stop it.)

We then want to send messages to the receiver::

  examples/send //localhost/receiver

You'll see a Hello, World message appear in STDOUT on the receiver!

Behind the scenes, what has happened is that the sender tells the
directory it has a message for a specific address, and the directory
redirects that message to the receiver. The directory essentially
separates the physical addresses of each entity from their logical
addresses.

Intermediaries
==============

Let's try setting up an intermediary service between the sender and
receiver. We'll set up a service that upper cases all the letters in a
message::

  examples/upper //localhost/transform //localhost/receiver &

This configures the upper service to receive messages at the
``/localhost/upper`` address, and forward its processed messages to
``//localhost/receiver``. (We cana run it as a background process
because this example doesn't output to STDOUT.)

Now, we can send a message to the upper service::

  examples/send //localhost/transform

We'll see that the original receiver receives a capitalized
message. We've just created an intermediary service! You can also send
a message directly to ``localhost/receiver`` and see that it bypasses
the upper service. The intermediary is completely transparent to the
receiver.

Load Balancing
==============

Let's now create a "lower" microservice by copying the upper
microservice, and changing the ``on_message`` event handler::

  def on_message(self, event):
      if hasattr(event.message.body, "lower"):
          event.message.body = event.message.body.lower()
      self.stream.put(event.message)

Instead of just starting the new service on a different service
address, let's start it up on the same transform address::

  examples/lower -p //localhost:5680 //localhost/transform //localhost/receiver &

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

In Datawire, we use the term dataflow to refer to your messaging
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

Code
====

So far, we've only discussed different ways to configure Datawire
microservices, but not how you actually write a microservice. Datawire
tries to make it as simple as possible for developers to write their
own microservices. Today, we include native support for Python and C,
with JavaScript and Ruby not too far behind.

Let's take a look at the receiver code. The receiver is implemented as
a service, which is just an ordinary process that binds to a local
port and accepts incoming AMQP connections. You can handle those
connections however you like. In this example we are simply printing
any incoming messages. Here's the receiver code in its entirety:

.. literalinclude:: ../../../examples/recv
   :language: python

Although clients can connect directly to a service if they know its
physical address, it's not a good idea to tie a service to a single
physical address. This address might change due to hardware or
network failures, or you may want to deploy additional instances of a
service for load balancing purposes.

Using a ``Tether``, our service can advertise its physical address
with a logical address in the Datawire directory. Clients can then
connect to the logical address and be routed to the service's physical
address. A ``Tether`` also keeps Datawire aware of the current status
of a service. If the service's process dies or becomes unresponsive
for any reason, the ``Tether`` will be broken, and the route will be
automatically dropped. This ensures clients are only routed to
functioning service instances.

We set up the ``Tether`` and physical address in ``__init__``:

.. literalinclude:: ../../../examples/recv
   :language: python
   :pyobject: Service.__init__

Datawire uses Apache Qpid Proton (see http://qpid.apache.org/proton)
to handle incoming messages. Proton provies a high performance,
asynchronous event dispatcher called the ``Reactor`` which natively
processes AMQP 1.0 messages. In the ``on_reactor_init`` function, we
initialize the ``Reactor``:

.. literalinclude:: ../../../examples/recv
   :language: python
   :pyobject: Service.on_reactor_init

Finally, we implement the ``on_message`` function which is called by
the ``Reactor`` when a new message arrives:

.. literalinclude:: ../../../examples/recv
   :language: python
   :pyobject: Service.on_message


