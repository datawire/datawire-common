.. _quick_start:

Quick Start
===========

At the end of this quick start you will use the promising features from above. Statement of what you are about to do. **FIXME** Figure out what to say here once we decide how much the quick start will cover.

Requirements
------------

* RHEL 7/CentOS 7 or Ubuntu 14.04 LTS.
* Run everything on one machine (localhost).
* Some http services, or use the `Greeting service from Spring <https://spring.io/guides/gs/rest-service/>`_
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

Once configured, launching Baker components is easy using your operating system's standard controls. On CentOS 7::

  $ systemctl start directory.service
  $ systemctl start sherlock.service
  $ systemctl start watson.service

On Ubuntu 14.04 LTS::

  $ service directory start
  $ service sherlock start
  $ service watson start

Next Subsection Name
--------------------

Access your service through Baker to verify things are working okay::

  $ curl http://localhost:8000/greeting

Steps
Links to reference documentation

Summary
-------

Next Steps
----------
