Datawire
========

Adopting a microservice architecture means, among other things, that
you're committed to building a distributed system. Building and
maintaining distributed systems can be hard and complex. Datawire is
designed to make it easier for you to build and maintain
microservices by providing a basic set of services that all your
microservices can use.

Datawire's underlying architectural assumption is that all
communication should be asynchronous. A microservice should be able to
fire a message off to a destination, and forget about that
message. Asynchronous communication adds resilience, since a sender no
longer needs to wait for a receiver to proceed.

Datawire uses AMQP 1.0, a language-independent, OASIS/ISO standard
messaging protocol, to provide asynchronous communication. Any AMQP
1.0-compliant broker or client can interact seamlessly with Datawire,
and Datawire itself depends on Apache QPid Proton, an open source AMQP
1.0 client.

By using AMQP 1.0 as its basic building block, Datawire enables you to
build more composable, resilient microservices faster. In the
subsequent tutorial and developer guide, you'll see how.
