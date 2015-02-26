Datawire Architecture
#####################

Overview
========

Datawire enables you to build a fully distributed microservices
architecture. What does this mean?

   **Messages can (but do not have to) flow asynchronously from any
   entity on the network directly to any other entity on the
   network.**

Entities can be anything on the Datawire network that can send or
receive messages. Common entity types include:

* *Microservices*, which process the content of messages. For example,
  a search microservice could index incoming messages, and send
  notifications when new items are added to the index.
  
* *Messaging intermediaries*, entities which do not inspect the content
  of a message, but can buffer, forward, or publish messages to other
  entities. For example, a queue is a type of messaging intermediary.
  
* *Client endpoints*, which interact with users. For example, a web
  browser client can directly send and receive messages on the
  Datawire network.

This basic concept where every entity on the network is a first class
citizen enables two design goals for Datawire:

1. Make microservice communication as easy to use as HTTP. HTTP has
   gained ubiquity in part because it's a point-to-point protocol,
   with no central dispatch mechanism -- just a global address
   mechanism enabled by DNS. Datawire is similar: there's a global
   addressing mechanism, and point-to-point messaging.

2. Expose the full capabilities of system built on asynchronous
   messaging. Asynchronous messaging enables greater resiliency,
   composability, and scalability, and Datawire aims to expose this
   functionality without compromising on ease of use.

The rest of this document will explore some of the design choices that
we've made to help achieve these goals. If you're impatient, feel free
to skip directly to the :ref:`tutorial`.
   
AMQP 1.0
========

Datawire leans heavily on the Advanced Messaging Queuing Protocol 1.0
specification, and uses `Apache Qpid Proton
<http://qpid.apache.org/proton>`_ as a robust, high performance
implementation of the AMQP 1.0 specification. Note that Datawire uses
1.0 and not 0.9.x, because 1.0 provides a much greater amount of
flexibility around messaging topologies. The 0.9.x specification was
written with a specific set of use cases, and codified some basic
messaging patterns directly into the specification. By using AMQP 1.0,
Datawire is able to support a full superset of the topologies
supported by AMQP 0.9.

The following section will walk through some of the core capabilities
of Datawire, and point to specific features of AMQP 1.0 that Datawire
is using to help implement these capabilities.

Application Level Networking
----------------------------

Datawire lets users create application-level virtual networks at the
message level, using `AMQP 1.0 Links
<http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-transport-v1.0-os.html#section-links>`_. Conceptually,
this is similar to virtual private networks that are defined at the
transport layer. Whereas VPNs are defined and managed by network
administrators, Datawire networks can be defined and managed by
applications and services, and operate at the application layer.

Composability
-------------

Datawire enables highly composable web services by allowing users to
create message processing pipelines, where the output of a
microservice can be passed on to one or more microservices, ad
infinitum. Datawire relies upon the notion of `settlement
<http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-transactions-v1.0-os.html#doc-idp145616>`_,
which transfers responsibility for message delivery to the next node
in the pipeline.

In traditional messaging systems, direct microservice chaining is not
possible -- instead, microservices need to adopt a hub-and-spoke model
where each microservice consumes messages from a central broker, and
then sends messages back to the central broker, creating a single
bottleneck and point of failure.

Polyglot
--------

Many early adopters of microservices have embraced the notion of
polyglot programming: using the best language and (and possibly
persistence strategy) for a given problem domain. Datawire uses AMQP
as its language-independent common message representation, enabling
microservices written in different languages and architectures to
communicate.

Resilience, Scale, and Performance
----------------------------------

Datawire uses the `flow control
<http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-transport-v1.0-os.html#doc-flow-control>`_
features of AMQP as a key mechanism to improve resilience, scale, and
performance. The credit-based flow control mechanism enables Datawire
to optimize the flow of messages between different entities on the
network based on the resource capacity of each entity. This helps
alleviate issues such as backpressure in your network, and maximizes
the total network throughput.

Note that Datawire provides many other mechanisms for resilience,
e.g., Datawire components can be started in any particular order,
which is essential for failure recovery.



 
