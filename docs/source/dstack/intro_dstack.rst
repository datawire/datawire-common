.. _dstack:

Overview
########

dstack consists of two components, a monitoring agent, Watson, and a routing
agent, Sherlock. dtack depends on haproxy.



Install
=======

Dstack installs on Linux. First, make sure HAProxy is installed. Then,
install dstack::

  pip install watson
  pip install sherlock

You'll also need to set up and deploy the directory service.::

  docker pull datawire/directory

Registering a new microservice
==============================

There is a single Watson instance per server, VM, or container (you
can deploy multiple microservices on a single server).

The main Watson configuration file is a single YAML file that points
to all the microservice configuration files on a given server.

Each microservice has its own configuration file.

#. Install Watson, and edit the watson.yaml file.
   * The watson.yaml file contains a list of directories to subscribe
     to, as well as a list of all the microservice configuration files
     on a given server.

#. Configure your microservice configuration file.
   * Health checks

#. Start Watson.


Connecting microservices
========================

Sherlock makes it easy to connect microservices.

There is a single Sherlock instance per server, VM, or container. (You
can deploy multiple microservices on a single server).

#. Configure the sherlock.yaml file.
   * The sherlock.yaml file contains a list of directories to
   subscribe to.
   * Also create a mapping between a local port and the services you
     want to connect to (e.g., the foo microservice)

#. Start Sherlock.

#. Update your code to talk to your local port, instead of the
   service. Restart your service if necessary for the changes to take
   effect.
   
#. Everything should work exactly as before.   


Upgrade microservice
====================

#. Deploy Watson on your new version of the microservice, with its own
   microservice.yaml file.

#. Configure the directory to route 10% of the traffic to the new
   microservice, per the version number::

     dw route add //monolith //barker_bizlogic(2) 10%

#. The directory will automatically route the remaining traffic to the
   primary instance(s).
