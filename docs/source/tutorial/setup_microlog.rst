.. Datawire.io documentation master file, created by
   sphinx-quickstart on Tue Jan 27 12:04:31 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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

We then register the microlog service with Datawire::

  dw service add microlog //example.com/microlog

We can start the microservice running locally::

  cd microlog; ./microlog.py //example.com/microlog

Finally, we can connect a client to the logging service::

  ./logger.py //example.com/microlog


