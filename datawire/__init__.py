# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

__author__    = "datawire.io <hello@datawire.io>"
__copyright__ = "Copyright (C) 2015 k736, inc."
__version__   = "0.3"

# So logging doesn't emit "No handlers could be found for logger" message.
import logging as _logging
_logging.getLogger("datawire").addHandler(_logging.NullHandler())

from .address import Address
from .agent import Agent
from .container import ancestors, Container
from .linker import Linker, Sender, Receiver, Tether
from .stream import Entry, Store, Stream
from .decoder import Decoder
from .processor import Processor
from .sampler import Sampler
from .configuration import Configuration
from .counts import Counts

from .impl import dual_impl
if dual_impl.dualImpls:
  print "Using java ", ", ".join(sorted(dual_impl.dualImpls))
del dual_impl