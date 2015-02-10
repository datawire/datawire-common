Datawire
========

Datawire is a distributed messaging network for microservices.
Datawire provides flexible routing topologies, service discovery, and
security. In Datawire, all communication is peer-to-peer and
fully asynchronous. 

Install
=======

Install the latest version of Datawire on Mac OS X or Linux::

  curl https://install.datawire.io | /bin/sh

This will install all the Datawire components, including the
microserver, command line interface, directory, and example
microservices. 

Initialization
==============

Once Datawire is installed, we can initialize and set up the system to
run locally with the ``init`` command::

  dw init

This will initialize the command line client, and start an instance of
the Directory locally.

Connecting Microservices
========================

This example will show how Datawire can be used to connect two
different microservices.

In this example, we'll use the order microservice example included in
the installation. The order microservice generates a random set of
orders. The invoicing microservice processes orders, and generates
invoices based on the orders.

We start the orders microservice, and tell it to send orders to the
invoices address::

  ./orders.py //example.com/invoices

You'll see a set of randomly generated orders scroll by every few
seconds on your terminal. However, these orders aren't going anywhere,
because we haven't started a microservice to process the orders.

We need to start the invoice microservice. In a new terminal window,
start the microservice, and bind it to a network-reachable address and
port::

  ./invoices.py //192.0.2.0:5672

You'll see that the invoices microservice starts, but it's not
receiving any messages. This is because we haven't mapped the physical
address of invoices to the invoices address. So, let's do that now::

  dw route add //example.com/invoices //192.0.2.0:5672

The invoices microservice will start showing the actual orders that
are being sent by the orders microservice.

Introspection
=============

We're going to take a brief detour and talk about a few built-in ways
to debug Datawire.

We can get a real-time list of all routes by subscribing to the
directory routing table. The directory publishes all ths information
as a message stream that any client can subscribe to. Because this is
a common operation, the dw command line client implements this as
a shortcut::

  dw status

Type Ctrl-C to exit, or you can leave it running in the background and
it will always show the latest routing table.

The directory also publishes a log stream. Similarly, any client can
subscribe to this message stream. You can subscribe to the log stream
with the dw client::

  dw listen directory

By exposing all of this data as a raw message stream, Datawire makes
it easy to write a microservice that processes or displays any of this
data.

Load Balancing
==============

Now let's try doing some more sophisticated routing. Suppose the
invoicing microservice starts to fall behind in processing orders. You
can deploy another instance of the invoicing microservice, and tell
the directory to load balance between the two invoicing
microservices::

  ./invoices.py //192.0.2.1:5672
  dw route add //example.com/invoices //192.0.2.1:5672

Note that the address is exactly the same as the original invoice
address, but we've added a separate network address that shares the
same Datawire address.

Now, when the orders microservice sends orders to the invoices
address, the messages will be randomly sent between the two invoices
order processors.

Because Datawire is dynamically routing the order messages, messages
will be routed only to live instances. This means you can elastically
add or remove instances to the address pool without worrying how it
will affect your load balancing.

Messaging Topologies
====================

Load balancing is a type of messaging topology: messages from the
orders service are sent once (and only once) to a pool of
recipients. A Datawire messaging topology describes the logical layout
of your message network: how each of your microservices are arranged
on the network, and how they communicate with each other.

Datawire is very flexible in configuring different types of message
topologies. The table below outlines some common topologies. We use
the term source to refer to the sender (e.g., orders in the example
above) and target to refer to the recipient (e.g., invoices).

+----------------+------------------------+---------------------+
|    Type        |      Description       |   Example           |
+================+========================+=====================+
|                |                        |                     |
|   Singleton    | Source can have 1 and  |  Chat microservice  |
|                | and only 1 target,     |  (you don't want    |
|                | guaranteeing a serial  |  your conversations |
|                | message sequence       |  to be chopped up)  |
+----------------+------------------------+---------------------+
|                |                        |                     |
|                | All targets receive    |  Classic pub/sub    |
|  Topic         | a copy of the same     |                     |
|                | message                |                     |
|                |                        |                     |
+----------------+------------------------+---------------------+

Service Routers
===============

Resilience
==========

