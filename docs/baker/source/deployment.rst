.. _deployment:

Deployment
==========

The following instructions explain how to set up and utilize Baker in a
typical environment. The instructions below assume that you have set up the
`Datawire repository on PackageCloud <https://packagecloud.io/datawire/staging/install>`_
on all relevant machines/vms.

On Enterprise Linux 7::

  $ curl -s https://packagecloud.io/install/repositories/datawire/staging/script.rpm.sh | sudo bash

On Ubuntu 14.04 LTS::

  $ curl -s https://packagecloud.io/install/repositories/datawire/staging/script.deb.sh | sudo bash



For simplicity, the examples assume a set of named servers, VMs, or
containers set up under the domain ``example.com``. Some pieces of the
system may want to run on stable resources; these are presented as
named machines, e.g., ``database.example.com``. Other pieces will
likely be deployed, upgraded, removed, etc. on an ongoing basis; these
would run on elastically-deployed resources named something like
``vm123.example.com``.

The example services themselves use HTTP to communicate, typically
running in an application server like Tomcat. An example service
called ``greeting`` running on the host ``vm678.example.com`` could be
accessed at the URL ``http://vm678.example.com/greeting``. Any HTTP
client would suffice. The command line examples will use ``curl`` but
each of the following is roughly equivalent::

  curl http://vm678.example.com/greeting
  lynx -dump http://vm678.example.com/greeting
  w3m -dump http://vm678.example.com/greeting
  wget -O - http://vm678.example.com/greeting

Directory
---------

The Datawire Directory is at the core of Baker. It should run on a
stable, reliable system that experiences relatively few interruptions.
In practice, the Directory is able to recover from server restarts
quickly and efficiently. The other components in Baker are designed to
handle a brief interruption of Directory availability without any
trouble. (For more details on this see the Baker :ref:`architecture`.)

The hostname of the Directory will appear in service URLs and so it
must have a well known stable hostname that is accessible to all
client and service nodes participating in your deployment.

Install the directory using the package tool appropriate for your
system::

  $ ssh directory.example.com

  directory $ sudo yum install datawire
   (or)
  directory $ sudo apt-get install datawire

Configure the directory with its well known and stable hostname as
follows::

  directory $ sudo cp directory.conf.proto directory.conf
  directory $ sudo nano directory.conf
  directory $ cat directory.conf
  [Directory]
  host: directory.example.com
  level: WARNING

Once the directory is configured, use the appropriate tool to start
it. On Enterprise Linux 7::

  directory $ sudo systemctl start directory.service

On Ubuntu 14.04 LTS::

  directory $ sudo service directory start

Sherlock
--------

Software that needs to use a service will use Sherlock to find and
access an instance of that service transparently. Such software might
be as simple as a command line HTTP tool like ``curl``, or it might be
a large, complicated system that needs access to dozens of services to
perform the core operations of a business.

Setting up Sherlock::

  $ ssh vm123.example.com

  vm123 $ sudo yum install datawire-baker
   (or)
  vm123 $ sudo apt-get install datawire-baker

Once baker is installed, edit the sherlock config to reference the
well known directory set up in the previous section::

  vm123 $ sudo cp sherlock.conf.proto sherlock.conf
  vm123 $ sudo nano sherlock.conf
  vm123 $ cat sherlock.conf
  [Sherlock]
  directory: //directory.example.com/directory
  proxy: /usr/sbin/haproxy
  rundir: /opt/datawire/run
  debounce: 2
  dir_debounce: 2

Now any process on your vm can access services by name without needing
to know where instances of the service are running::

  vm123 $ curl http://localhost:8000/<service-name>

By going through HAProxy, each live instance of a service is accessed
in round-robin fashion. If an instance drops out, e.g., for
maintenance, Watson notifies the directory, which allows Sherlock to
update the HAProxy configuration and keep requests flowing through the
remaining instances. When that instance comes back, Sherlock again
makes the appropriate adjustments to haproxy. New instances get added
to the pool automatically in much the same way.

Watson
------

Service instances that want to be dynamically accessible will use
watson to advertise their presence to the datawire directory. Watson
must run colocated on the same machine/vm as the service instance.
Watson will periodically check the health of the service instance and
register its location and status with the directory.

Setting up Watson::

  $ ssh vm101.example.com

  vm101 $ sudo yum install datawire-baker
    (or)
  vm101 $ sudo apt-get install datawire-baker

Once baker is installed, edit the watson config to:

#. Reference the well known directory set up in the previous section.
#. Specify the logical service name for clients.
#. Provide a physical service address that is accessible from all
   client nodes.
#. Provide a url for health checks.

::

  vm101 $ sudo cp watson.conf.proto watson.conf
  vm101 $ sudo nano watson.conf
  vm101 $ cat watson.conf
  [Watson]
  directory: //directory.example.com/directory
  address: //directory.example.com/<service-name>
  url: http://vm101.example.com:9001/<service-name>
  liveness: http://vm101.example.com:9001/<service-name>/health
  period: 3  ; seconds between liveness checks

Please note that if you have multiple instances for the same service,
the url and liveness check will be different for each instance.

More Services
-------------

As your system grows in complexity, your network of microservices will
grow as well. Some services will only offer access to a resource but
not utilize other services in the system. However, many services will
benefit from using other services too. It is common to end up with a
network of communicating services. Baker makes it easy for
microservices to communicate with each other, and other Datawire
components help to organize, manage, and understand the complicated
topologies that may arise.

**FIXME** What to do with the above?
