.. Datawire.io documentation master file, created by
   sphinx-quickstart on Tue Jan 27 12:04:31 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Datawire Security Architecture
==============================

The Datawire security architecture is a "zero trust" security model
where security is ubiquitous throughout the infrastructure. In this
model, there is no perimeter, and authentication and trust are
established on a per session basis.

Authentication
--------------

The authentication model for Datawire services is a Trust On First Use
(TOFU) model that is conceptually similar to ssh. The authentication
workflow is described below:

User wants to connect microservice A to microservice B.

#. When A is started, it generates a public/private key pair
   (https://rietta.com/blog/2012/01/27/openssl-generating-rsa-key-from-command/).

#. A sends Auth request to B.

#. B sends back a challenge.

#. A sends a signed message to B containing::

   - Organization name
   - Microservice name
   - Public key
   - Public key algorithm name
   - Signature

   where signature is::

   - Organization name
   - Microservice name
   - Public key
   - Public key algorithm name
   - Challenge

#. B validates the signed message using the supplied public key.

#. If the public key is not in B's database, B generates a control
   message asking for approval of the connection (TOFU). Control message
   sent to the registered owner(s) of B.

#. If approved, A can then connect to B.

When a new instance of the service is started, it needs to get a copy
of the public/private keypair from an existing instance. 

Service routers can also copy the key.





Wire Level Protection
---------------------

All traffic is encrypted using TLS, with Elliptic Curve Diffie Hellman
(ECDHE) used for key exchange. This has several benefits:

- perfect forward secrecy
- no need to manage SSL certificates




