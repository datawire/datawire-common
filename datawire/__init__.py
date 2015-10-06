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

from _metadata import *

# So logging doesn't emit "No handlers could be found for logger" message.
import logging as _logging
_logging.getLogger("datawire").addHandler(_logging.NullHandler())

from .address import Address
from .agent import Agent
from .container import ancestors, Container
from .linker import Linker, Sender, Receiver, Tether
from .stream import Entry, Store, Stream, MultiStore
from .decoder import Decoder
from .processor import Processor
from .sampler import Sampler
from .configuration import Configuration
from .counts import Counts

from .impl import dual_impl
if dual_impl.dualImpls:
  print "Using java ", ", ".join(sorted(dual_impl.dualImpls))
del dual_impl