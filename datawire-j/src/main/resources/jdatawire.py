
import os

# Probable interaction with python io package...
# in some cases the io.datawire package later gets removed,
# so grab a reference to the module

import io.datawire as io_datawire

from proton import WrappedHandler, _chandler
from org.apache.qpid.proton.engine import BaseHandler

import proton

class NamedProperty(object):
    _fullname = None
    _name = None

    def __get__(self, instance, clazz=None):
        if instance is None:
            return self
        if self._name is None:
          try:
            cls = clazz or instance.__class__
            self._name = self.myname(cls)
          except:
            import traceback
            traceback.print_exc()
            raise
        return self.get(instance)

    def myname(self, clazz):
        for clz in clazz.__mro__:
            for name, value in clz.__dict__.iteritems():
                if value is self:
                    self._fullname = clz.__module__ + "." + clz.__name__ + "." + name
                    return name
        return "*unknown*"

    def get(self, instance):
        raise AttributeError(self._fullname + " did not implement get()")

class ExtendedProperty(NamedProperty):
    def __init__(self, accessor, converter):
        self.accessor = accessor
        self.converter = converter

    def get(self, instance):
        impl = vars(instance).get("_impl", None)
        if impl is None:
            raise AttributeError(self._name + " has no _impl")
        value = self.accessor.get(impl.impl)
        if value is None:
            raise AttributeError(self._name + " is not in record")
        converted = self.converter(value)
        instance.__dict__[self._name] = converted
        return converted

class NamedSettableProperty(NamedProperty):
    def __set__(self, instance, value):
        if self._name is None:
            self._name = self.myname(instance.__class__)
        self.set(instance, value)

    def set(self, instance, value):
        raise AttributeError(self._fullname + " did not implement set()")

class WrappedHandlerProperty(NamedSettableProperty):
    def get(self, instance):
        return getattr(instance._impl, self._name)

    def set(self, instance, value):
        setattr(instance._impl, self._name, value)

def wrap_proton_message(impl):
    wrapper = proton.Message()
    wrapper._msg.decode(impl)
    wrapper._post_decode()
    return wrapper


proton.Event.message = ExtendedProperty(io_datawire.DatawireEvent.MESSAGE_ACCESSOR, wrap_proton_message)

def unwrap_handler(delegate):
    if delegate is not None:
        if isinstance(delegate, BaseHandler):
            return delegate
        else:
            return _chandler(delegate)
    else:
        return None

class Decoder(WrappedHandler):

    def __init__(self, delegate=None):
        def datawire_decoder():
            args = []
            args.append(unwrap_handler(delegate))
            return io_datawire.Decoder(*args)
        WrappedHandler.__init__(self, datawire_decoder)

class Processor(WrappedHandler):

    def __init__(self, delegate=None, window=None):
        def datawire_processor():
            args = []
            args.append(unwrap_handler(delegate))
            if window is not None:
                args.append(window)
            ret = io_datawire.Processor(*args)
            return ret
        WrappedHandler.__init__(self, datawire_processor)

class Sampler(WrappedHandler):

    def __init__(self, delegate=None, frequency=None):
        def datawire_sampler():
            args = []
            args.append(unwrap_handler(delegate))
            if frequency is not None:
                args.append(frequency)
            return io_datawire.Sampler(*args)

        WrappedHandler.__init__(self, datawire_sampler)

    frequency = WrappedHandlerProperty()


class _Reactive:
  def start(self, reactor):
    self._impl.start(reactor._impl)

  def stop(self, reactor):
    self._impl.stop(reactor._impl)

class _Linker(_Reactive):
  linked = WrappedHandlerProperty()


class Sender(WrappedHandler, _Linker):
  def __init__(self, target, *handlers, **kwargs):
    def datawire_sender():
      args = []
      args.append(target);
      args.append(kwargs.pop("source", None))
      args.append(map(unwrap_handler, handlers))
      if handlers:
        pass
      if kwargs: raise TypeError("unrecognized keyword arguments: %s" % ", ".join(kwargs.items()))
      return io_datawire.Sender(*args)
    WrappedHandler.__init__(self, datawire_sender)

  def send(self, o):
    self._impl.send(o)

  def close(self):
    self._impl.close()

class Receiver(WrappedHandler, _Linker):
  def __init__(self, source, *handlers, **kwargs):
    def datawire_receiver():
      args = []
      args.append(source);
      args.append(kwargs.pop("target", None))
      args.append(kwargs.pop("drain", False))
      args.append(map(unwrap_handler, handlers))
      if handlers:
        pass
      if kwargs: raise TypeError("unrecognized keyword arguments: %s" % ", ".join(kwargs.items()))
      return io_datawire.Receiver(*args)
    WrappedHandler.__init__(self, datawire_receiver)

class Tether(WrappedHandler, _Reactive):
    def __init__(self, directory, address, target, host=None, port=None, policy=None, agent_type=None):
      def datawire_tether():
        args = [directory, address, target, host, port, policy, agent_type]
        return io_datawire.Tether(*args)
      WrappedHandler.__init__(self, datawire_tether)

class Linker(_Reactive):
  def __init__(self):
    self._impl = io_datawire.Linker()

class Stream(WrappedHandler):
  def __init__(self, store=None):
    def datawire_stream():
      args = []
      if store is not None:
        args.append(store)
      return io_datawire.Stream(*args)
    WrappedHandler.__init__(self, datawire_stream)

DatawireEvent = io_datawire.DatawireEvent

class Store(io_datawire.impl.TransientStore):
  def __init__(self, name=None):
    super(Store,self).__init__(name)

  def put(self, msg, persistent=True, address=None):
    if isinstance(msg, basestring):
      import java.nio.ByteBuffer
      msg = java.nio.ByteBuffer.wrap(msg, len(msg), 0)
      msg.flip()
    self.super__put(msg, address)

class DualImpl:
    impls = dict(
      Address=io_datawire.Address,
      Decoder=Decoder,
      Processor=Processor,
      Sampler=Sampler,
      Counts=io_datawire.Counts,
      Sender=Sender,
      Receiver=Receiver,
      Tether=Tether,
      Stream=Stream,
      Store=Store,
      MultiStore=io_datawire.impl.MultiStoreImpl,
      Linker=Linker,
    )

    dualImpls = set()

    ignore = frozenset(filter(None, os.environ.get("JDATAWIRE_DISABLE", "").split(",")))

    def __call__(self, clazz):
        name = clazz.__name__
        if name in self.impls and not self.ignore.intersection((name, "*")):
          self.dualImpls.add(name)
          return self.impls[name]
        else:
          return clazz

dual_impl = DualImpl()
del DualImpl
