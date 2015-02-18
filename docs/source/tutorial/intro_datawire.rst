Datawire
========

Datawire is a distributed messaging network for microservices.
Datawire provides flexible routing topologies, service discovery, and
security. In Datawire, all communication is fully asynchronous.

Install
=======

Datawire installs on Linux, and requires a basic toolchain to
install. On a yum-based systems, install the following packages::

  yum install gcc libuuid-devel openssl-devel swig python-devel unzip
  tar make patch cmake
 
On an apt-based system, install the following packages::

  apt-get install curl gcc uuid-dev libssl-dev swig python-dev unzip
  make patch cmake

Then, install the latest version of Datawire on Mac OS X or Linux::

  curl http://www.datawire.io/install.sh | /bin/sh

This will install into the `datawire-XX` directory all Datawire
components, including the microserver, command line interface,
directory, and example microservices.

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

This -f ("follow") method subscribes to messages from the directory on the
addition/deletion of new routes.

Now, let's set up a receiver for the messages::

  examples/recv //localhost/foo

This starts a program that listens for messages at the address
``//localhost/foo``. Note that this is a *logical* address, not a
physical one. If you go over to the route list window, you'll
see a route has appeared. (And if you stop the recv process by typing
Ctrl-C, you'll see the route disappears. Start the recv process again
if you stop it.)

We then want to send messages to the receiver::

  examples/send //localhost/foo

You'll see a Hello, World message appear in STDOUT on the receiver!

Behind the scenes, what has happened is that the sender tells the
directory it has a message for a specific address, and the directory
redirects that message to the receiver. The directory essentially
separates the physical addresses of each entity from their logical
addresses.

now, start up another instance of recv

//recv -p //localhost:3000 //localhost/foo

Load Balancing
==============

Now let's try doing some more sophisticated routing. Let's support
randomized load balancing between the receivers. To do this, we start
another receiver process, registered to the same address::

  examples/recv -p //localhost:5679 //localhost/foo

The -p flag here tells the receiver to use a different physical
address, since this receiver can't run on the same physical address as
the original receiver. The logical address remains the same.

Now, we can just run the same send command several times to the foo
address::

  examples/send //localhost/foo
  examples/send //localhost/foo

You'll see the Hello, World message randomly appear in one of the two
receiver instances.

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
