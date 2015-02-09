.. Datawire.io documentation master file, created by
   sphinx-quickstart on Tue Jan 27 12:04:31 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Step 0.  Install Datawire
=========================

Install the latest version of Datawire on Mac OS X or Linux::

  curl https://install.datawire.io | /bin/sh

This will install the Datawire microserver, command line interface,
message bus, and an example logging microservice.

Step 1.  Set up microlog
========================

We're going to start by setting up a simple logging microservice with
Datawire. This service is simple, but will come in handy for
debugging.

To start, we need to first initialize our command line client::

  dw init

This will prompt you to enter an email address and password. The
command line client will generate a public/private key pair which will
be stored locally in the ``.dw/`` directory. The private key is
encrypted using your password.

We then need to pick an address for the microlog service, and
associate the microlog service with the given address. In Datawire,
addressing looks like a URL, e.g., ``//foo.example.com/microlog/``::

  dw service add microlog //<<ADDRESS>>

We can start the microservice running locally::

  cd microlog; ./microlog.py //<<ADDRESS>>

Finally, we can connect a client to the logging service::

  ./logview //<<ADDRESS>>

The client will display all messages that are received by the microlog
service. 

TODO: What sends messages to the logger?

----

Screencast

- set up install
- python program that sends a constant stream of data
- show that it is in the receiver
- kill the directory; data still goes through
- john wants to write a test receiver as well to process this data in prod
- forks the data
- tests in live production
- python/javascript


- show code that sends a message without a broker (this is cool)
- wiretap or transform
- then do request/response, pub/sub






------

1. dw init
   - creates public/private keys
   - starts up directory
   - sets up public key as owner in the directory

2. dw listen amqp://directory shows log files

3. start up your client in a new terminal window

   dw listen amqp://foo.bar/asdf

   - binds to which IP?
   - connects to the directory with a tether

4. dw send amqp://foo.bar/asdf <message> (or cat foo.txt | dw send)

5. add dwcap to route

   - dw service add dwcap amqp://foo.bar/dwcap
   - dw route add amqp://foo.bar/asdf amqp://foo.bar/dwcap
     (add 
   - ./dwcap

6. dw send message, see it's capitalized

   - you can send other messages to the route
   - you can also add other destinations that use dwcap

7. resilience example

   - take down dwcap
   - send a message; it doesn't show up yet on the receiver
   - put dwcap up
   - see all caps message

8. ok, so this all cool stuff from the command line, what about some code?



dw send
dw listen

dw route 




1. dw microserver (receive) bind amqp://foo.bar/asdf/ on amqp port on localhost
   - binds to the host/port
   - connects to the directory with a tether
2. dw send to amqp://foo.bar/asdf/
3. dw subscribe to debug port on directory
4. dw status
5. capitalization microservice
6. content-based routing




3. create session; kill -9


1. map microlog to directory address
2. dw 

2. dw status shows realtime status
3. dw debug subscribe microlog to show stuff that shows up in the log
4. dw debug send to address will show up in microlog
5. show off work queue, pub/sub (topic)
   - add new routing rule
   - start up another instance of microlog
   - add new routing rule
   - start up another instance of microlog
6. show javascript client



dw debug send
