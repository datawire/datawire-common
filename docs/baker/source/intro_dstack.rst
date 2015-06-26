.. _dstack:

Baker
#####

Why use Baker?
==============

**Richard's document**

Deploying Baker
===============

**Richard's document**

How Baker Works
===============

**Conceptual Model: Rafi**

Quick Start **Abhay**
===========

At the end of this quick start you will use the promising features from above. Statement of what you are about to do. **FIXME** Figure out what to say here once we decide how much the quick start will cover.

Requirements
------------

* RHEL 7/CentOS 7 or Ubuntu 14.04 LTS.
* Run everything on one machine (localhost).
* Some http service, or use the Greeting service from Spring
* **FIXME** Probably want sentences here...

Verify access to your service using a web browser or a command line tools like ``curl``. For the Greeting service::

  $ wget -q https://github.com/spring-guides/gs-rest-service/archive/master.zip
  $ unzip -q master.zip
  $ cd gs-rest-service-master/complete/
  $ mvn -q package
  $ java -jar target/gs-rest-service-0.1.0.jar > /dev/null 2>&1 &
  $ curl http://localhost:8080/greeting
  {"id":3,"content":"Hello, World!"}

Install
-------

On CentOS 7, add access to the `Datawire repository on PackageCloud <https://packagecloud.io/datawire/staging/install>`_ and use ``yum`` to perform the installation::

  $ curl -s https://packagecloud.io/install/repositories/datawire/staging/script.rpm.sh | sudo bash
  $ sudo yum install datawire-baker

On Ubuntu 14.04 LTS, add access to the `Datawire repository on PackageCloud <https://packagecloud.io/datawire/staging/install>`_ and use ``apt-get`` to perform the installation::

  $ curl -s https://packagecloud.io/install/repositories/datawire/staging/script.deb.sh | sudo bash
  $ sudo apt-get install datawire-baker

Configure
---------

OS ``service`` commands can control Baker once ``/etc/datawire`` has the appropriate configuration files. Sample files are installed there. Replicate those and edit them to look like this::

  $ cd /etc/datawire
  $ cp directory.conf.proto directory.conf
  $ cp sherlock.conf.proto sherlock.conf
  $ cp watson.conf.proto watson.conf
  $ nano directory.conf sherlock.conf watson.conf
   [...]

  $ cat directory.conf
  [Directory]
  host: localhost
  level: WARNING

  $ cat sherlock.conf
  [Sherlock]
  directory: //localhost/directory
  proxy: /usr/sbin/haproxy
  rundir: /opt/datawire/run
  debounce: 2
  dir_debounce: 2

  $ cat watson.conf
  [Watson]
  directory: //localhost/directory
  address: //localhost/service-name
  url: http://localhost:8080/greeting
  liveness: http://localhost:8080/greeting/liveness_check
  period: 3  ; seconds between liveness checks

Launch
------

Once configured, launching Baker components is easy using your operating system's standard controls::

  $ service directory start
  $ service sherlock start
  $ service watson start





Steps
Links to reference documentation

Summary
-------

Next Steps
----------

Deployment Procedures
=====================
Canary Testing
--------------
Load Balancing
--------------
Upgrades
--------

Architecture
============

Reference **Abhay**
=========

Directory
---------
Watson
------
Sherlock
--------













**Remnants of older stuff follows.**


Design and Architecture
=======================

Baker is patterned after `AirBnb's SmartStack
<http://nerds.airbnb.com/smartstack-service-discovery-cloud/>`_ which
is an excellent piece of software and design. The aforereferenced
blog post gives a terrific overview of the different approaches to
service discovery and routing, which we generally agree with (hence,
our adoption of the overall approach).

Baker does make several different design decisions than SmartStack.

#. Baker isolates its use of HAProxy from the user. We did this
   because HAProxy supports HTTP and TCP, but does not natively
   support other protocols. In particular, HAProxy does not support
   any async messaging protocols, which are important for certain use
   cases in microservices.
#. Baker uses the Datawire Directory service instead of
   Zookeeper. Zookeeper provides a strongly consistent model; the
   Directory service focuses on availability. This also simplifies
   Baker deployment.
#. **FIXME** Need more items ...
#. ... to qualify as "several."
#. Maybe change to "a few" or "a couple" or similar?

That having been said, the basics are very similar. Baker's Sherlock
facilitates the service client role in a microservices architecture. It
is analogous to SmartStack's Synapse; it keeps a local HAProxy instance
updated with all live services in the Directory. Baker's Watson keeps
the Directory aware of the liveness of its associated service, much like
SmartStack's Nerve, thereby facilitating the service role.

In summary, any running instance that *consumes* services will use
Sherlock, running locally on the same server, VM, or container, to find
and access those services transparently. Any running instance that
*offers* services will use Watson to advertise those services to the
network. It is, of course, reasonable for one service to use another;
that instance will simply have both Sherlock and Watson running
alongside on the same server/VM/container.

Section Title FIXME
===================

The following instructions explain how to set up and utilize Baker in a
typical environment. For simplicity, the examples assume a set of named
servers, VMs, or containers set up under the domain ``example.com``.
Some pieces of the system may want to run on stable resources; these are
presented as named machines, e.g., ``database.example.com``. Other
pieces will likely be deployed, upgraded, removed, etc. on an ongoing
basis; these would run on elastically-deployed resources named something
like ``vm123.example.com``.

The example services themselves use HTTP to communicate, typically
running in an application server like Tomcat. An example service called
``emitter`` running on the host ``vm678.example.com`` could be accessed
at the URL ``http://vm678/emitter``. Any HTTP client would suffice. The
command line examples will use ``curl`` but each of the following is
roughly equivalent::

  curl http://vm678/emitter
  lynx -dump http://vm678/emitter
  w3m -dump http://vm678/emitter
  wget -O - http://vm678/emitter

Directory
=========

The Datawire Directory service is at the core of Baker. It should run on
a stable, reliable system that experiences relatively few interruptions.
We will install it on ``services.example.com``::

  $ ssh services.example.com

  services $ sudo yum install datawire-directory
       (or)
  services $ sudo apt-get install datawire-directory

  services $ directory -n services -a //services/directory

**FIXME** *The above is largely nonsense. We need to talk about
configuration. Something like:* Edit ``/etc/datawire.d/directory``, set
the ``hostname`` field to ``services`` and the ``address`` field to
``//services/directory``. Then use ``sudo svc datawire-directory
restart`` to get things running.

In practice, the Directory service is able to recover from server
restarts quickly and efficiently. The other components in Baker are
designed to handle a brief interruption of Directory service
availability without any trouble. **FIXME** *Brief?*

Watson
======

Let's consider a service called ``emitter``, instances of which run on
some varying set of resources, such as ``vm101.example.com`` through
``vm120.example.com``. In other words, it is possible to reach an instance of ``emitter`` as follows::

  curl http://vm109/emitter

The ``emitter`` service does not utilize any other services in the
example.com network; it is used by other parts of the system to access a
resource (static data, computation, credit card validation, etc.) To
enable other parts of the system to use ``emitter``, deploy Watson as
part of the process of deploying ``emitter``::

  $ ssh vm101.example.com

  vm101 $ sudo yum install datawire-watson
    (or)
  vm101 $ sudo apt-get install datawire-watson

  vm101 $ watson -d //services/directory //services/emitter http://vm101/emitter 3

The options given to Watson indicate that the service is available on
the URL ``http://vm101/emitter``, that it should be checked for liveness
every three seconds, and that it should be advertised as ``emitter`` on
the Directory that handles the ``//services`` namespace.

Other resources also offering instances of ``emitter`` would configured
slightly differently::

  vm113 $ watson -d //services/directory //services/emitter http://vm113/emitter 3

Each instance of Watson advertises the same service name to the same
directory, but tracks a distinct instance of the service itself. This
particular Watson will access the URL
``http://vm113/emitter/liveness_check`` every three seconds to determine
the status of this instance of ``emitter`` and will update the Directory
as needed.

**FIXME** Mention ``dw -d //services/directory route list`` or not?

Sherlock
========

Software that needs to use a service will use Sherlock to find and
access an instance of that service transparently. Such software might be
as simple as a command line HTTP tool like ``curl``, or it might be a
large, complicated system that needs access to dozens of services to
perform the core operations of the business. Let's consider as our
example service client a piece of software called ``core-business`` that
runs on ``main.example.com``. It uses ``emitter`` and other services,
but is not a service itself.

Set up Sherlock on ``main.example.com``::

  $ ssh main.example.com

  main $ sudo yum install datawire-sherlock
   (or)
  main $ sudo apt-get install datawire-sherlock

  main $ sherlock -d //services/directory

Now processes on ``main.example.com`` can access services by name
without needing to know where instances of the service are running::

  main $ curl http://localhost:8000/emitter

The ``core-business`` program would work the same way, connecting to
port 8000 on the local machine and allowing HAProxy to handle the
details of reaching the correct destination.

By going through HAProxy, each live instance of ``emitter`` is accessed
in round-robin fashion. If an instance drops out, e.g., for maintenance,
Watson notifies the directory, which allows Sherlock to update the
HAProxy configuration and keep requests flowing through the remaining
instances. When that instance comes back, Sherlock again makes the
appropriate adjustments to haproxy. New instances get added to the pool
automatically in much the same way.

More Services
=============

As your system grows in complexity, your network of microservices will
grow as well. Some services will be like ``emitter``, offering access to
a resource but not utilizing any other services in the system. However,
many services will benefit from using other services too. It is common
to end up with a network of communicating services. Baker makes it easy
for microservices to communicate with each other, and other Datawire
components help to organize, manage, and understand the complicated
topologies that may arise.

Let's consider a service called ``transform`` that uses the output of
``emitter`` to produce a different result. For example, if ``emitter``
is responsible for producing a current weather map for a location, then
``transform`` could take that image and produce a smaller,
mobile-friendly version. The ``core-business`` code would access map
images from ``emitter`` and from ``transform`` in similar ways (via
Baker), but ``transform`` would also access ``emitter`` directly (again
via Baker).

Deployment of ``transform`` involves deploying both Sherlock and Watson
alongside. Sherlock allows ``transform`` to access other services, such
as ``emitter``, while Watson allows other parts of the system, such as
``core-business``, to access ``transform``.

**FIXME** Do we really need another set of instructions/examples?

Installation is identical to the above. if ``transform`` runs on
vm201.example.com through vm220.example.com::

  $ ssh vm201.example.com

  vm201 $ sudo yum install datawire-sherlock datawire-watson
    (or)
  vm201 $ sudo apt-get install datawire-sherlock datawire-watson

  vm201 $ sherlock -d //services/directory
  vm201 $ watson -d //services/directory //services/transform http://vm201/transform 3

Now ``transform`` is accessible from any host running Sherlock, such as
``main.example.com``::

  main $ curl http://localhost:8000/transform

**FIXME** Say something about microservice pipelines, typical service
topology, etc.

Incremental Upgrade Rollout
===========================

Deploying an upgrade of a heavily-used, mission-critical service can be
a daunting task. Baker enables a staged or incremental upgrade rollout
process that can avoid much of the risk associated with a hard cutover
to a new version. This incremental approach is known as *Canary Testing*
and by a few other names. `Martin Fowler's Bliki entry
<http://martinfowler.com/bliki/CanaryRelease.html>`_ covers it in
detail.

Let's say there are twenty instances of ``emitter`` version 1.03 running
on the ``vm101.example.com`` through ``vm120.example.com``. The new
``emitter`` version 2.0 has passed all of its testing and is ready to be
deployed. We can start by bringing down a single ``emitter`` instance,
say on ``vm103.example.com``, upgrading it, and restarting it. Thanks to
Baker, clients of ``emitter`` would not experience any downtime during
the upgrade process.

At this point, one out of every twenty accesses to ``emitter`` will
reach the version 2.0 instance on ``vm103.example.com``. This is an
opportunity to monitor the upgraded ``emitter`` in the production
environment for as long as is desired. If there are any problems, simply
bring down the version 2.0 instance on ``vm103.example.com`` and Baker
will take care of keeping things running uninterrupted. If things go
smoothly, the rest of the ``emitter`` instances can be upgraded
incrementally in the same way.


Overview
########

Microservices need to send data back and forth to each other. Because
microservice instances tend to be elastic, hard-coding in physical
addresses for a given microservice address does not work. Instead, a
*service discovery* framework can map between logical names and
physical addresses.


dstack consists of two components, a monitoring agent, Watson, and a routing
agent, Sherlock. dstack depends on haproxy.

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
