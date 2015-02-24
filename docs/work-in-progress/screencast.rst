Screencast
----


- set up install
- python program that sends a constant stream of data
- show that it is in the receiver
- kill the directory; data still goes through
- john wants to write a test receiver as well to process this data in prod
- forks the data
- tests in live production
- python/javascript


screencast demo items
-------

amqp

* how easy it is to send an async message (fire and forget)
* type system & multiple languages
* broker-less (p2p)
* performance
* flow control

datawire

* in-line transform
* wiretap
* messaging topologies
  * intermediated messaging
    * pub/sub
  *



introducing datawire

- you're building an ecommerce website

- here's a simple python microservice
  - it gets orders
  - stores orders as python objects
  - you have invoices

EASY EASY EASY
    
- POINT: Easy to send async message
  - Show some python code
  - No broker!

- POINT: any language
  - Receive in JavaScript
  - Deserialize object in JavaScript (type system)

DATA FLOW
    
- POINT: think about your microservices as a set of data flows
  - Show a visualization of data flow

- POINT: messaging topologies
  - pub/sub, queuing, etc.
  
- POINT: Flow control
  - Animation (traffic lights)

