Authentication Notes
====================

## Threat vectors

- Network based
  - Traffic analysis
  - Sniffing
- Client/User targeted
  - Authentication
- Host based
  - Remote host exploitation

## Summary

TLS is used to secure each AMQP connection. SASL, with digest
authentication, is used for authentication.

Users are authenticated using username/password authentication, with
the password sent over TLS.

Protecting against client/user attacks
======================================

## Authentication entities

- Users: self explanatory
- Clients: need API key access
  - mapped to users (someone needs to manage them)

## Authentication protocol

- User authentication uses basic authentication
  - username/password sent over encrypted channel
  - password is securely hashed using pbkdf2 in database
  - possibly use passlib to simplify implementation

- Client authentication uses HTTP Digest authentication
  - generate API key + secret
  - hmac(nonce, timestamp, auth version, request metadata, secret)

Use HTTP Digest authentication.

How AWS does it:

http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
http://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html

How Duo does it with HTTP digest

https://www.duosecurity.com/docs/authapi#authentication

## SCRAM

- Client authentication could also use SCRAM
  - advantage is that it hosts proofs the server
  - http://legastero.github.io/Suelta/ might help

## Session Types

Authentication happens upon a client connection (e.g., TCP connection)
or a user creates a session (e.g., user login, git authentication).

- User session
- Connection

## Key values

- source IP address
- application
- user
- expiry
- version

