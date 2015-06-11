.. _dstack:

Overview
########

Microservices need to send data back and forth to each other. Because
microservice instances tend to be elastic, hard-coding in physical
addresses for a given microservice address does not work. Instead, a
*service discovery* framework can map between logical names and
physical addresses.


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
   * The watson.yaml file contains a list of Directories to connect
     to
   * It also contains a list of all the config files for the
     microservices on a server
   * By convention, we put the microservices config files in /etc/datawire.d/

#. Configure your microservice configuration file.
   * Add the URL suffix that will route to the microservice, e.g.,
     barker.internal.
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

#. Start Sherlock.

#. Update the URLs that you use in your code to route through
   Sherlock. In a Sherlock URL, the domain should be the local
   Sherlock address and port. By default, Sherlock routes HTTP through
   port 5432, giving a domain of ``localhost:5432``. The Sherlock URL
   path is the name of the specific microservice that you want to
   access. 

   When specifying the URL, the domain should be the local Sherlock
   address, which,


    By default, Sherlock routes HTTP through port 5432. This
   can be changed in the sherlock.yaml file.

   For example, http://barker.internal.example.com should be
   remapped to "localhost:5432/barker.internal".

#. Everything should work exactly as before. Connections will be
   automatically routed to the microservice that is registered (by
   Watson) as barker.internal.

Create routes
=============

The directory lets you manage routes. So, let's start by adding a new
HTTP route.

#. dw route add //monolith //barker.internal 30%

   or do we do something like this

   dw route add //barker.internal //instance2 30%



   microservice advertises itself as "barker"
   it also needs a host
   you need to figure out the default mapping between barker and host


   default is
     - 100% goes to host
     - then if you have a second host, you round robin
     - but then how do you not add a host to the pool for canary etc?


Upgrade microservice
====================

#. Deploy Watson on your new version of the microservice, with its own
   microservice.yaml file.

#. Configure the directory to route 10% of the traffic to the new
   microservice, per the version number::

     dw route add //monolith //barker_bizlogic(2) 10%

#. The directory will automatically route the remaining traffic to the
   primary instance(s).

Load balance microservice
=========================

