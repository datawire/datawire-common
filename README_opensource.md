Datawire
========

Datawire makes it easy to quickly build and manage resilient and
scalable microservices
(http://martinfowler.com/articles/microservices.html).

With Datawire, you:

- write a microservice using Python, JavaScript, C, or Java
- deploy the microservice, using any technology

Datawire provides infrastructure that lets you:

- Discover other available microservices
- Communicate asynchronously with other microservices and clients
- Manage your microservices
- Authenticate microservices

Detailed documentation is available at http://docs.datawire.io.

Quick Start
===========

Install Datawire and example microchat:

  curl https://install.datawire.io | /bin/sh

Add the microchat to Datawire:

  dw service add microlog

Start the Python log microservice:

  cd microlog; ./microlog.py

Connect a JavaScript client to the microlog:

  https://localhost:3423/

Introduction
============

Properly architected, a microservices architecture enables teams to
develop complex software systems, faster, with greater
reliability. Unfortunately, the basic infrastructure to bootstrap a
microservices architecture is extensive, requiring significant DevOps
expertise and development effort to deploy and integrate.

The key to a robust microservices architecture is an asynchronous
messaging system -- once you've decoupled your application into a
bunch of microservices, they need to talk to each other. Datawire
provides an easy-to-use, flexible architecture for microservices to
communicate.

Datawire is built on the AMQP 1.0 messaging standard, and embeds Qpid
Proton to send and receive AMQP messages. Datawire consists of three
core components:

- Microserver, a lightweight server that connects your microservice
  to other microservices and clients
- Service router, a stateful router that operates on application level
  (Layer 7) data
- Directory, a distributed service that connects microservices to each
  other

Resilient Architecture
======================

Datawire lets you build a *resilient* architecture. In a resilient
architecture, failures are expected, and failures have limited or zero
impact on the overall system.

For example, imagine an ecommerce store where ordering has been
decoupled into several microservices. Once an order is placed,
information about that order might go to the invoicing microservice,
the fulfillment microservice, and a warranty registration
microservice.

Using a synchronous protocol such as HTTP creates a brittle system,
where the order microservice needs to sequentially call each dependent
microservice. Not only does the order microservice need to know about
each of these other services, but it also needs to handle the
situation where a service fails to respond (typically with timeouts,
which moves the problem to the end user).

Instead of trying to write 100% reliable microservices, you can use
asynchronous messaging. By setting up a publish/subscribe messaging
topology[1], the order microservice publishes a message and forgets
about the message once it's published. The invoicing, fulfillment, and
registration microservices subscribe to the order microservice. If one
of the microservices is temporarily unavailable, the messaging service
can hold the message until it becomes available. This creates
resiliency: a failure in one of your microservices does not impact the
end user.

More
====

In the real world, there are many different types of failures, and
Datawire provides ways to increase your overall system
resilience. Datawire also provides integrated service discovery,
application-level data routing, and security.

To learn more:

Twitter: @datawireio
Github: https://github.com/datawire
Docs: http://docs.datawire.io

[1] Asynchronous messaging is a broad category, and not every
asynchronous message technology supports this particular topology,
which is more precisely described as a stateful publish/subscribe
topology with multiple consumers.


Other
=====

TBD if to include:


Datawire does not help you deploy microservices (you should use
Docker, Chef, Vagrant, EC2), nor does it help with running your
microservices (you should look at Mesos, Kubernetes, Fleet).



Datawire operates at the *application* level. As such, it imposes no
constraints on your deployment infrastructure. You can use Datawire
with Docker, Kubernetes, bare metal servers, in AWS, or with your own
data center, or any combination thereof.

