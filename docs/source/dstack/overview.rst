Baker
=====

Baker is a service discovery and routing system, designed to simplify 
deploying microservices.

Why use Baker?
==============

Suppose you have two services, A and B, that communicate with each
other. For reliability, imagine that A and B are deployed on four
separate instances, A1-A4 and B1-B4 for availability and scalability. 

Baker solves several problems:

#. Service discovery. Requests from A to B automatically locate an
   available server instance running the B service.
#. Load balancing. Requests from A to B are automatically distributed
   between all available instances of B.
#. Upgrades and testing. New versions of a microservice can be
   easily introduced by adding a new server instance to the service
   pool. Load will be distributed to the new version, and old
   instances can be turned off as new ones are introduced to the pool.

Deploying Baker
===============

Baker deploys as a separate process next to your application. You then
update your application to talk to Baker, instead of directly to
another application. This approach means that Baker can integrate with
any application architecture, written in any language.
   
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





