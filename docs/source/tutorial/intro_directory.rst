Directory
=========

The Datawire Directory is a distributed directory that maps entities
to addresses. The Directory redirects incoming connections to the
appropriate entity based on address. As such, no messages actually
flow through the Directory.

Install
=======

Install the latest version of Datawire on Mac OS X or Linux::

  curl https://install.datawire.io | /bin/sh

This will install the Datawire microserver, command line interface,
message bus, and an example microservice.

Initialization
==============

Once Datawire is installed, we can initialize and set up the system to
run locally with the ``init`` command::

  dw init

This will initialize the command line client, and start an instance of
the Directory locally.

Connecting Microservices
========================

This example will show how the Directory can be used to connect two
different microservices.

In this example, we'll use the order microservice example included in
the installation. The order microservice generates a random set of
orders. The invoicing microservice processes orders, and generates
invoices based on the orders.

We'll start by registering each of our microservices with the
directory::

  dw service add orders //example.com/orders
  dw service add invoices //example.com/invoices

These commands map an entity name to a specific address.

Now, we need to add a route between these two microservices::

  dw route add //example.com/orders //example.com/invoices

This command tells the directory that messages from the orders address
should flow to the invoices address. Note that this command is order
sensitive, as all routes are asynchronous, and hence, one way (we'll
talk about how to do a request/response route later).

Now, we can verify that this works by starting both the orders and
invoices services in separate terminal windows::

  ./examples/orders.py //example.com/orders
  ./examples/invoices.py //example.com/invoices

You'll see a list of orders being randomly created in the orders
terminal, and you'll see the same set of orders appear in the invoices
terminal.

Debugging
=========

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

Load Balancing
==============

Now let's try doing some more sophisticated routing. Suppose the
invoicing microservice starts to fall behind in processing orders. You
can deploy another instance of the invoicing microservice, and tell
the directory to load balance between the two invoicing microservices::

  dw service add invoice2 //example.com/invoices

Note that the address is exactly the same as the original invoice
address.

Datawire will automatically load balance between the two instances
based on the credit-based flow control mechanism built into AMQP.

Subscriptions
=============
