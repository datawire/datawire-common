# Copyright 2015 datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import itertools
import io
try:
  import io.datawire as io_datawire
except:
  # Probable interaction with python io package...
  # in some cases the io.datawire package later gets removed,
  # so grab a reference to the module
  import io.datawire.Address
  import io.datawire.impl.EventImpl
  import sys
  io_datawire = sys.modules["io.datawire"]

from proton import WrappedHandler, _chandler
from org.apache.qpid.proton.engine import BaseHandler

import proton
from proton.wrapper import Wrapper

class NamedProperty(object):
    _fullname = None
    _name = None

    def __get__(self, instance, clazz=None):
        if instance is None:
            return self
        if self._name is None:
          cls = clazz or instance.__class__
          self._name = self.myname(cls)
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

class NamedSettableProperty(NamedProperty):
    def __set__(self, instance, value):
        if self._name is None:
            self._name = self.myname(instance.__class__)
        self.set(instance, value)

    def set(self, instance, value):
        raise AttributeError(self._fullname + " did not implement set()")

class ExtendedProperty(NamedSettableProperty):
    def __init__(self, accessor, converter, peeler):
        self.accessor = accessor
        self.converter = converter
        self.peeler = peeler

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

    def set(self, instance, value):
        impl = vars(instance).get("_impl", None)
        if impl is None:
            raise AttributeError(self._name + " has no _impl")
        if value is not None:
          peeled = self.peeler(value)
        else:
          peeled = value
        self.accessor.set(impl.impl, peeled)

class WrappedHandlerProperty(NamedSettableProperty):
    def get(self, instance):
        return getattr(instance._impl, self._name)

    def set(self, instance, value):
        setattr(instance._impl, self._name, value)

def wrap_proton_message(impl):
    if impl is None:
      return None
    wrapper = proton.Message()
    wrapper._msg.decode(impl)
    wrapper._post_decode()
    return wrapper

def peel_proton_message(wrapper):
    if wrapper is None:
      return None
    wrapper._pre_encode()
    wrapper._msg.pre_encode()
    return wrapper._msg.impl

proton.Event.message = ExtendedProperty(io_datawire.DatawireEvent.MESSAGE_ACCESSOR, wrap_proton_message, peel_proton_message)

def unwrap_handler(delegate):
    if delegate is not None:
        if isinstance(delegate, BaseHandler):
            return delegate
        else:
            return _chandler(delegate)
    else:
        return None

class Decoder(WrappedHandler):

    def __init__(self, delegate=None, *handlers):
        def datawire_decoder():
            children = []
            args = [children]
            if delegate is not None:
              children.append(unwrap_handler(delegate))
            children.extend(map(unwrap_handler, handlers))
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


class WrappedSender(WrappedHandler, _Linker):
  def __init__(self, impl_or_constructor):
    WrappedHandler.__init__(self, impl_or_constructor)

  @staticmethod
  def _sender_args(target, *handlers, **kwargs):
    args = []
    args.append(target);
    args.append(kwargs.pop("source", None))
    args.append(map(unwrap_handler, handlers))
    if handlers:
      pass
    if kwargs: raise TypeError("unrecognized keyword arguments: %s" % ", ".join(kwargs.items()))
    return args

  def send(self, o):
    self._impl.send(o)

  def close(self):
    self._impl.close()

class Sender(WrappedSender):
  def __init__(self, target, *handlers, **kwargs):
    def datawire_sender():
      args = self._sender_args(target, *handlers, **kwargs)
      return io_datawire.Sender(*args)
    WrappedSender.__init__(self, datawire_sender)

class WrappedReceiver(WrappedHandler, _Linker):
  def __init__(self, impl_or_constructor):
    WrappedHandler.__init__(self, impl_or_constructor)

  @staticmethod
  def _receiver_args(source, *handlers, **kwargs):
    args = []
    args.append(source);
    args.append(kwargs.pop("target", None))
    args.append(kwargs.pop("drain", False))
    args.append(map(unwrap_handler, handlers))
    if kwargs: raise TypeError("unrecognized keyword arguments: %s" % ", ".join(kwargs.items()))
    return args

class Receiver(WrappedReceiver):
  def __init__(self, source, *handlers, **kwargs):
    def datawire_receiver():
      args = self._receiver_args(source, *handlers, **kwargs)
      return io_datawire.Receiver(*args)
    WrappedReceiver.__init__(self, datawire_receiver)

class Tether(WrappedHandler, _Reactive):
    def __init__(self, directory, address, target, host=None, port=None, policy=None, agent_type=None):
      def datawire_tether():
        args = [directory, address, target, host, port, policy, agent_type]
        return io_datawire.Tether(*args)
      WrappedHandler.__init__(self, datawire_tether)

    @property
    def directory(self):
      return self._impl.directory

    @property
    def agent(self):
      return self._impl.agent

class FakeSendersCollection():
  def __init__(self, linker):
    self._linker = linker

  def __len__(self):
    return self._linker._impl.sendersSize()

class FakeSendersProperty(object):
  def __get__(self, instance, clazz=None):
    if instance is None:
      return self
    return FakeSendersCollection(instance)

class Linker(_Reactive):
  def __init__(self):
    self._impl = io_datawire.Linker()

  def sender(self, target, *handlers, **kwargs):
    args = WrappedSender._sender_args(target, *handlers, **kwargs)
    return WrappedSender.wrap(self._impl.sender(*args))

  senders = FakeSendersProperty()
  
  def close(self):
    self._impl.close()

class Stream(WrappedHandler):
  def __init__(self, store=None):
    def datawire_stream():
      args = []
      if store is not None:
        args.append(Store._peel(store))
      return io_datawire.Stream(*args)
    WrappedHandler.__init__(self, datawire_stream)

DatawireEvent = io_datawire.DatawireEvent

def peel(wrapped):
  if wrapped is None:
    return None
  return getattr(wrapped, "_impl", wrapped)

class jStore(io_datawire.impl.TransientStore):
  def __init__(self, wrapper, name=None):
    self._wrapper = wrapper
    super(jStore,self).__init__(name)

  def put(self, msg, address):
    self._wrapper.put(msg, address=address)

  def compact(self, tail):
    return map(peel, self._wrapper.compact(map(Entry, tail)))

  def gc(self):
    return self._wrapper.gc()

  def flush(self):
    return self._wrapper.flush()

class jMultiStore(io_datawire.impl.MultiStoreImpl):
  def __init__(self, wrapper, name=None):
    self._wrapper = wrapper
    super(jMultiStore,self).__init__(name)

  def put(self, msg, address):
    self._wrapper.put(msg, address=address)

  def compact(self, tail):
    return map(peel, self._wrapper.compact(map(Entry, tail)))

  def gc(self):
    return self._wrapper.gc()

  def flush(self):
    return self._wrapper.flush()
  
  def resolve(self, address):
    return Store._peel(self._wrapper.resolve(address))

class Store(object):
  @classmethod
  def _peel(cls, store):
    if store is None:
      return None
    if isinstance(store, cls):
      return store._impl
    raise TypeError("Not a store")

  def __init__(self, name=None):
    self._impl = jStore(self, name)

  def put(self, msg, persistent=True, address=None):
    self._impl.super__put(message_or_buffer(msg), address)

  def gc(self):
    return self._impl.super__gc()

  def flush(self):
    return self._impl.super__flush()

  def reader(self, address=None):
    return Reader(self._impl.reader(address))

  def compact(self, tail):
    return itertools.imap(Entry, self._impl.super__compact(map(peel, tail)))

def message_or_buffer(msg):
    if isinstance(msg, basestring):
      import java.nio.ByteBuffer
      msg = java.nio.ByteBuffer.wrap(msg, len(msg), 0)
      msg.flip()
    return msg

class MultiStore(Store):
  def __init__(self, name=None):
    self._impl = jMultiStore(self, name)
    
  def resolve(self, address):
    return Store()

class Reader:
  def __init__(self, impl):
    self._impl = impl

  def more(self):
    return self._impl.more()

  def next(self):
    return Entry.wrap(self._impl.next())
  
  def close(self):
    self._impl.close()

class Entry:
  @classmethod
  def wrap(cls, impl):
    if impl is None:
      return None
    return cls(impl)

  def __init__(self, msg, persistent=True, deleted = False):
    if isinstance(msg, io_datawire.impl.EntryImpl):
      self._impl = msg
    else:
      self._impl = io_datawire.impl.EntryImpl(message_or_buffer(msg), persistent, deleted)

  @property
  def message(self):
    bytes = self._impl.encodedMessage
    return bytes.array()[bytes.position() : bytes.position() + bytes.limit()].tostring()
  
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
      MultiStore=MultiStore,
      Linker=Linker,
      Entry=Entry,
      ancestors=io_datawire.Container.ancestors,
    )

    dualImpls = set()
    have = frozenset(impls)
    ignore = frozenset(filter(None, map(str.strip, os.environ.get("JDATAWIRE_DISABLE", "").split(","))))

    def __call__(self, clazz=None, depends=[]):
      def decorate(clazz):
        name = clazz.__name__
        reqs = set((name,)).union(depends)
        if not reqs.difference(self.have) and not self.ignore.intersection(reqs.union(set("*"))):
          self.dualImpls.add(name)
          return self.impls[name]
        else:
          return clazz
      if clazz is None:
        return decorate
      else:
        return decorate(clazz)

dual_impl = DualImpl()
del DualImpl
