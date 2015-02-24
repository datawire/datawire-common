Messaging Topologies
====================

Load balancing is a type of messaging topology: messages from the send
service are sent once (and only once) to a pool of receivers. In
Datawire, the term messaging topology refers to the logical layout of
your message network: how each of your microservices are arranged on
the network, and how they communicate with each other.

Datawire is very flexible in configuring different types of message
topologies. The table below outlines some common topologies. We use
the term source to refer to the sender (e.g., orders in the example
above) and target to refer to the recipient (e.g., invoices).

message streams or flows

properties associated with your to: address

intersetion of address & node

+----------------+------------------------+---------------------+
|    Type        |      Description       |   Example           |
+================+========================+=====================+
|                |                        |                     |
|   Singleton    | Source can have 1 and  |  Chat microservice  |
|                | and only 1 target,     |  (you don't want    |
|                | guaranteeing a serial  |  your conversations |
|                | message sequence       |  to be chopped up)  |
|                |                        |                     |
+----------------+------------------------+---------------------+
|                |                        |                     |
|                | All targets receive    |  Classic pub/sub    |
|   Topic        | a copy of the same     |                     |
|                | message                |                     |
|                |                        |                     |
+----------------+------------------------+---------------------+

Service Routers
===============

Resilience
==========

