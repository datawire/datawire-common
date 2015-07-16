
import io
import sys
print [m for m in sys.modules.iteritems() if m[0].startswith("io")]
from io.datawire import Address
from io.datawire import Decoder as io_datawire_Decoder
from io.datawire import Event
print [m for m in sys.modules.iteritems() if m[0].startswith("io")]

from proton import WrappedHandler


print Address

class Decoder(WrappedHandler):

    def __init__(self, delegate = None):
        WrappedHandler.__init__(self, datawire_decoder)
        if delegate:
          self.add(delegate)
        
def datawire_decoder():
    return io_datawire_Decoder()