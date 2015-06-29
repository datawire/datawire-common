Usage
=====

Canary Testing
--------------

**C&P vvvvv This seems to cover the other two items as well**

Deploying an upgrade of a heavily-used, mission-critical service can be
a daunting task. Baker enables a staged or incremental upgrade rollout
process that can avoid much of the risk associated with a hard cutover
to a new version. This incremental approach is known as *Canary Testing*
and by a few other names. `Martin Fowler's Bliki entry
<http://martinfowler.com/bliki/CanaryRelease.html>`_ covers it in
detail.

Let's say there are twenty instances of ``emitter`` version 1.03 running
on the ``vm101.example.com`` through ``vm120.example.com``. The new
``emitter`` version 2.0 has passed all of its testing and is ready to be
deployed. We can start by bringing down a single ``emitter`` instance,
say on ``vm103.example.com``, upgrading it, and restarting it. Thanks to
Baker, clients of ``emitter`` would not experience any downtime during
the upgrade process.

At this point, one out of every twenty accesses to ``emitter`` will
reach the version 2.0 instance on ``vm103.example.com``. This is an
opportunity to monitor the upgraded ``emitter`` in the production
environment for as long as is desired. If there are any problems, simply
bring down the version 2.0 instance on ``vm103.example.com`` and Baker
will take care of keeping things running uninterrupted. If things go
smoothly, the rest of the ``emitter`` instances can be upgraded
incrementally in the same way.

**C&P ^^^^^**

Load Balancing
--------------

Upgrades
--------
