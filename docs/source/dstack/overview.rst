Baker
=====

Baker is a service discovery and routing system designed for
microservice architectures.

Why use Baker?
==============

Suppose you have two microservices, A and B, that communicate with
each other. For scalability and availability, both microservices are
deployed on multiple servers (or containers).

Baker solves several problems:

#. Service discovery. Requests from A to B automatically locate an
   available instance of the B microservice.

#. Load balancing. Requests from A to B are automatically distributed
   between all available instances of B, without requiring a central
   load balancer in front of B.
   
#. Upgrades and testing. New versions of a microservice can be
   easily introduced by adding a new server instance to the service
   pool. Load will be distributed to the new version, and old
   instances can be turned off as new ones are introduced to the pool.


Deploying Baker
===============

Baker runs on any modern flavor of Linux. Baker works with any
application or microservice, regardless of programming
language. Usually, you just need a small configuration change in your
microservice to start using Baker.

How Baker Works
===============

Baker consists of three main components:

* Sherlock, which is responsible for routing a microservice's
  connections to the right destination
* Watson, which provides real-time liveness detection of a given
  microservice
* the Datawire Directory, which keeps track of all microservices and
  their associated routes

Sherlock and Watson are deployed on every microservice container or
server. Each microservice is then configured to proxy its connections
through Sherlock (behind the scenes, we use the super-reliable,
super-fast HAProxy). Sherlock uses information from the Directory to
route connections to the appropriate destination.

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
   cases in microservics.
#. Baker uses the Datawire directory service instead of
   Zookeeper. Zookeeper provides a strongly consistent model; the
   directory service focuses on availability. This also simplifies
   Baker deployment.

The Baker architecture is fully distributed, and resilient to the
failure of any component. 



