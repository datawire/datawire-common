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
