.. _quick_start:

Quick Start
===========

Ready to dive right in? This page will take you through deploying Baker in a minimal environment and then using it for load balancing and upgrading a simple service.

You will need an Enterprise Linux 7 (RHEL 7, CentOS 7, etc.) or Ubuntu 14.04 LTS machine, JDK 1.8 and Maven 3+ for the simple service, and about 15 minutes of your time.

Setup
-----

The sample deployment shown here will run everything on ``localhost``. The :ref:`deployment` section of this manual covers how to set things up in a production environment.

The simple service in this example is the Greeting service from `Spring's RESTful Web Service Guide <https://spring.io/guides/gs/rest-service/>`_. Set up that service::

  $ curl https://github.com/spring-guides/gs-rest-service/archive/master.zip -LO
  $ unzip -q master.zip
  $ cd gs-rest-service-master/complete/
  $ mvn -q package
  $ env SERVER_PORT=9001 java -jar target/gs-rest-service-0.1.0.jar > /dev/null 2>&1 &

**Note**: Running Maven without the ``-q`` option generates a lot of output, which may be helpful if there are any problems with the build process.

Verify access to the Greeting service using a web browser or a command line tool like ``curl``::

  $ curl http://localhost:9001/greeting
  {"id":1,"content":"Hello, World!"}

The ``id`` field in the output is a counter. If you hit the service repeatedly, that field will increment. Once set up, Watson will monitor this service by accessing it periodically, causing the counter to increment in the background.

Install
-------

On Enterprise Linux 7, add access to the `Datawire repository on PackageCloud <https://packagecloud.io/datawire/staging/install>`_ and use ``yum`` to perform the installation::

  $ curl -s https://packagecloud.io/install/repositories/datawire/staging/script.rpm.sh | sudo bash
  [...]
  $ sudo yum install datawire-baker

On Ubuntu 14.04 LTS, add access to the `Datawire repository on PackageCloud <https://packagecloud.io/datawire/staging/install>`_ and use ``apt-get`` to perform the installation::

  $ curl -s https://packagecloud.io/install/repositories/datawire/staging/script.deb.sh | sudo bash
  [...]
  $ sudo apt-get install datawire-baker

Configure
---------

Baker looks for its configuration files in ``/etc/datawire``. Sample files are installed there. Replicate those and edit them to look like this::

  $ cd /etc/datawire
  $ sudo cp directory.conf.proto directory.conf
  $ sudo cp sherlock.conf.proto sherlock.conf
  $ sudo cp watson.conf.proto watson.conf
  $ sudo nano directory.conf sherlock.conf watson.conf
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
  address: //localhost/greeting
  url: http://localhost:9001/greeting
  liveness: http://localhost:9001/greeting
  period: 3  ; seconds between liveness checks

Launch
------

Once configured, launching Baker components is easy using your operating system's standard controls. On Enterprise Linux 7::

  $ sudo systemctl start directory.service
  $ sudo systemctl start sherlock.service
  $ sudo systemctl start watson.service

On Ubuntu 14.04 LTS::

  $ sudo service directory start
  $ sudo service sherlock start
  $ sudo service watson start

Access your service through Baker to verify things are working okay::

  $ curl http://localhost:8000/greeting
  {"id":17,"content":"Hello, World!"}

Watson notifies the Directory that the Greeting microservice on ``http://localhost:9001/`` is running. Sherlock sets up HAProxy to route ``greeting`` requests to that microservice. Your ``curl`` above gets proxied to the right place. Note that your ``id`` field will likely be a different value, depending on how long Watson has run and how many times you accessed the service manually.

Load Balancing
--------------

Let's add more Greeting microservice instances for load balancing::

  $ cd /path/to/gs-rest-service-master/complete/
  $ env SERVER_PORT=9002 java -jar target/gs-rest-service-0.1.0.jar > /dev/null 2>&1 &
  $ env SERVER_PORT=9003 java -jar target/gs-rest-service-0.1.0.jar > /dev/null 2>&1 &

We will need to add a Watson instance for each one. Normally, you would run one microservice per server, VM, or container; see the :ref:`deployment` section for more detail. For this quick start, we have run them all on the same host, so we must run corresponding Watson instances manually::

  $ watson -d //localhost/directory -l http://localhost:9002/greeting //localhost/greeting http://localhost:9002/greeting 3 > /dev/null 2>&1 &
  $ watson -d //localhost/directory -l http://localhost:9003/greeting //localhost/greeting http://localhost:9003/greeting 3 > /dev/null 2>&1 &

Sherlock and HAProxy will automatically and transparently load balance over these three microservice instances because they all have the same service name ``//localhost/greeting``. The ``curl`` command above will access each of them in turn::

  $ for i in 1 2 3 4 5 ; do curl http://localhost:8000/greeting ; echo ; done
  {"id":18,"content":"Hello, World!"}
  {"id":16,"content":"Hello, World!"}
  {"id":54,"content":"Hello, World!"}
  {"id":19,"content":"Hello, World!"}
  {"id":17,"content":"Hello, World!"}

Upgrade
-------

Let's upgrade the Greeting service. Duplicate the Greeting service tree and edit line 11 in ``GreetingController.java``::

  $ cd ../..
  $ mkdir v2
  $ cd v2
  $ unzip -q ../master.zip
  $ cd gs-rest-service-master/complete/
  $ nano src/main/java/hello/GreetingController.java
  $ grep -n Hello src/main/java/hello/GreetingController.java
  11:    private static final String template = "Hello 2.0, %s!";
  $ mvn -q package

Instead of upgrading all of Greeting to the new version, let's perform a *canary test*. Roll out one new instance of Greeting 2.0 and its associated Watson::

  $ env SERVER_PORT=9004 java -jar target/gs-rest-service-0.1.0.jar > /dev/null 2>&1 &
  $ watson -d //localhost/directory -l http://localhost:9004/greeting //localhost/greeting http://localhost:9004/greeting 3 > /dev/null 2>&1 &

Baker will direct a subset of all traffic to that new instance automatically::

  $ for i in 1 2 3 4 5 ; do curl http://localhost:8000/greeting ; echo ; done
  {"id":112,"content":"Hello, World!"}
  {"id":77,"content":"Hello, World!"}
  {"id":75,"content":"Hello, World!"}
  {"id":6,"content":"Hello 2.0, World!"}
  {"id":113,"content":"Hello, World!"}

Let your upgraded Greeting service soak test as long as is desired. Problems? Just kill Greeting 2.0; Baker will keep the requests flowing. Everything going smoothly? Upgrade the remaining instances one at a time without any interruption of service.

Summary
-------

Congratulations on making your way through the Baker quick start! You've seen that Baker can be deployed quickly and easily, in many cases with no changes to your service. You've used Baker to perform load balancing and a safe upgrade with no interruption of service.

Next Steps
----------

#. Read about :ref:`deployment`, which shows how you would deploy Baker over your network of microservices.
#. Learn more about Baker's :ref:`architecture`.
