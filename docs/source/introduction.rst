Introduction to Datawire
########################

Microservice architectures can bring many benefits: greater
development velocity, more efficient resource utilization, better
code reuse, and the ability to use different languages and tools
for different tasks. Microservices can also be hard: they're
distributed systems and they require new skills and DevOps
infrastructure to deploy.

Datawire is designed to give you the benefits of microservices while
giving you a set of tools that manage the complexity. Datawire lets
you build composable, resilient microservices quickly and
easily. Intended for software developers, Datawire takes care of the
intricacies of building a distributed system so developers can just
focus on the code they need to write. Used in conjunction with rapid
deployment technologies such as Docker and CoreOS (although you
certainly don't have to), Datawire enables you to deploy a
sophisticated microservice architecture that can scale up or down as
your needs grow or shrink.

  "... the power of a system comes more from the relationships among
  programs than from the programs themselves."

 *Brian Kernigan and Rob Pike, The Unix Programming Environment, 1984*

We believe very much in the `Unix Philosophy
<http://en.wikipedia.org/wiki/Unix_philosophy>`_, and apply the
general approach to both the design of Datawire itself, and developers
using Datawire. In particular, Datawire enables composability of
microservices through a common message format and defined IO streams,
just as Unix enables composability of utilities through plain text as
a common message format and `pipes
<http://en.wikipedia.org/wiki/Unix_philosophy>`_ for communication.

In the subsequent pages, we'll talk about what we mean by
composability and resilience, and how Datawire lets you achieve those
goals. 
