.. _deployment:

Deployment
==========

**C&P vvvvv**

In summary, any running instance that *consumes* services will use
Sherlock, running locally on the same server, VM, or container, to find
and access those services transparently. Any running instance that
*offers* services will use Watson to advertise those services to the
network. It is, of course, reasonable for one service to use another;
that instance will simply have both Sherlock and Watson running
alongside on the same server/VM/container.

[...]

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

**C&P ^^^^^**

Directory
---------

**C&P vvvvv**

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

**C&P ^^^^^**

Sherlock
--------

**C&P vvvvv Note: this was written to go after the Watson section**

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

**C&P ^^^^^**

Watson
------

**C&P vvvvv Note: this was written to go before the Sherlock section**

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

**C&P ^^^^^**

**C&P vvvvv This doesn't fit the new outline, but takes the example a little further and might be worthy of consideration**

More Services
-------------

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

**C&P ^^^^^**
