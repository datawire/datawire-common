Reactor API Tutorial
####################

The reactor provides a general purpose event processing library for
writing reactive programs. A reactive program is defined by a set of
event handlers. An event handler is any class or object that defines
the ``on_<event>`` methods that it cares to handle.

Initializing and Exiting the Reactor
====================================

Here is a basic program that prints Hello, World when initialized.

.. literalinclude:: hello-world.py
   :language: python

The ``on_reactor_init`` method is roughly analogous to a ``main``
method. The reactor also produces an event when it is about to exit,
``on_reactor_final``. This event is guaranteed to happen last, and
will always happen regardless of program execution.

.. literalinclude:: goodbye-world.py
   :language: python
   :pyobject: Program.on_reactor_final

Scheduling
==========

You can schedule a task event for some point in the future, which will
cause the reactor to run until it has a chance to process the event.

.. literalinclude:: scheduling.py
   :language: python
   :pyobject: Program

You can also pass in a separate object to the scheduler. In this
example, we have a counter that prints its value every quarter second.

.. literalinclude:: counter.py
   :language: python

The reactor makes it easy to concurrently process multiple events. In
this example, we've added an additional event that prints a random
number every half second.

.. literalinclude:: count-randomly.py
   :language: python
   :pyobject: Program


Handlers
========

The ``on_unhandled`` event is called when an event occurs and the
event handler doesn't have an ``on_<event>`` method. This can be
useful not only for debugging, but for logging and for delegation and
inheritance.

.. literalinclude:: unhandled.py
   :language: python
   :pyobject: Program.on_unhandled

You can pass multiple handlers to the reactor when it is
constructed. These handlers will see every event the reactor
sees. Combined with the ``on_unhandled`` event, you can create a
simple reactor logger.

.. literalinclude:: reactor-logger.py
   :language: python

This logger doesn't see every event, however, becuase the reactor
event handler doesn't see every event. For example, scheduled tasks
may have a separate handler. The reactor implements a
``global_handler`` that sees every event.

.. code-block:: python
		
   r.global_handler.add(Logger())
   r.run()


Events know how to dispatch themselves to handlers. By combining this
with ``on_unhandled``, you can provide a kind of inheritance between
handlers using delegation.

.. literalinclude:: delegates.py
   :language: python

When an event dispatches itself to a handler, it also checks if that
handler has a ``handlers`` attribute and dispatches the event to any
children. 
   
.. literalinclude:: handlers.py
   :language: python

Selectors
=========

.. literalinclude:: echo.py
   :language: python

Tornado
=======

We'll walk through how the reactor can integrate with an external
event loop. We'll use `Tornado <http://www.tornadoweb.org>`_ as our
example framework.

.. literalinclude:: tornado-hello-world.py
   :language: python

The TornadoApp integrates a reactor into Tornado's ``ioloop``, and is
a good that combines the different handlers and selectors previously
discussed.

.. literalinclude:: tornado_app.py
   :language: python


