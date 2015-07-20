
# Probable interaction with python io package...
# in some cases the io.datawire package later gets removed, so grab references to stuff needed at runtime

from io.datawire import Address
from io.datawire import Processor as io_datawire_Processor
from io.datawire import Decoder as io_datawire_Decoder
from io.datawire import Event
from io.datawire.impl import EventImpl as io_datawire_impl_EventImpl

from proton import WrappedHandler, _chandler
from org.apache.qpid.proton.engine import BaseHandler

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
        if value is None:
            raise AttributeError(self._name + " is not in record")
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

proton_Event.message = ExtendedProperty(io_datawire_impl_EventImpl.MESSAGE, wrap_proton_message)

class Decoder(WrappedHandler):

    def __init__(self, delegate = None):
        def datawire_decoder():
            if delegate is not None:
                if isinstance(delegate, BaseHandler):
                    return io_datawire_Decoder(delegate)
                else:
                    return io_datawire_Decoder(_chandler(delegate))
            else:
                return io_datawire_Decoder()
        WrappedHandler.__init__(self, datawire_decoder)

class Processor(WrappedHandler):

    def __init__(self, delegate = None, window = None):
        def datawire_processor():
            args = []
            if delegate is not None:
                if isinstance(delegate, BaseHandler):
                    args.append(delegate)
                else:
                    args.append(_chandler(delegate))
            else:
                args.append(None)
            if window is not None:
                args.append(window)
            ret = io_datawire_Processor(*args)
            return ret
        WrappedHandler.__init__(self, datawire_processor)
        

class Impls:
    Address = Address
    Decoder = Decoder
    Processor = Processor

impls = Impls()
del Impls
