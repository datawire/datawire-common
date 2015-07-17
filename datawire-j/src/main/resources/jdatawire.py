
import io
import sys
print [m for m in sys.modules.iteritems() if m[0].startswith("io")]
from io.datawire import Address
from io.datawire import Decoder as io_datawire_Decoder
from io.datawire import Event
print [m for m in sys.modules.iteritems() if m[0].startswith("io")]

from proton import WrappedHandler

from proton import Event as proton_Event
from proton import Message as proton_Message

class ExtendedProperty(object):
  _name = None
  def __init__(self, accessor, converter):
    self.accessor = accessor
    self.converter = converter
  def __get__(self, instance, clazz):
    if instance is None:
      return self
    if self._name is None:
      self._name = self.myname(clazz)
    record = vars(instance).get("_record", None)
    if record is None:
      raise AttributeError(self._name + " has no _record")
    value = self.accessor.get(record)
    converted = self.converter(value)
    instance.__dict__[self._name] = converted
    return converted
   
  def myname(self, clazz):
    for clz in clazz.__mro__:
      for name, value in clz.__dict__.iteritems():
        if value is self:
          return name
    return "*unknown*"

def wrap_proton_message(impl):
  wrapper = proton_Message()
  wrapper._msg.decode(impl)
  wrapper._post_decode()
  return wrapper

proton_Event.message = ExtendedProperty(io.datawire.impl.EventImpl.MESSAGE, wrap_proton_message);


print Address

class Decoder(WrappedHandler):

    def __init__(self, delegate = None):
        WrappedHandler.__init__(self, datawire_decoder)
        if delegate:
          self.add(delegate)
        
def datawire_decoder():
    return io_datawire_Decoder()

class Impls:
    Address = Address
    Decoder = Decoder

impls = Impls()
del Impls
