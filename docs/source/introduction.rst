Introduction to Datawire
########################

Adopting a microservice architecture means, among other things, that
you're committed to building a distributed system. Building and
maintaining distributed systems can be hard and complex. Datawire
provides infrastructure that makes it much easier for you to build and
maintain microservices without thinking about the nuances of a
distributed system.

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

Using asynchronous messaging as its basic building block, Datawire
enables you to build composable, resilient microservices
faster. Datawire also lets you start thinking about your microservices
in terms of its **dataflow** -- how messages and data flow between
different parts of your system. In the subsequent tutorial and
documentation, we'll see how these concepts can help you build
smarter, better microservices.

