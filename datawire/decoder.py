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

import sys, traceback
from proton import EventType, Message, Delivery

from .impl import dual_impl, DatawireEvent

ENCODED_MESSAGE = EventType("encoded_message", DatawireEvent.Type.ENCODED_MESSAGE)
MESSAGE = EventType("message", DatawireEvent.Type.MESSAGE)

@dual_impl
class Decoder:

    def __init__(self, *handlers):
        self.__message = Message()
        self.handlers = handlers

    def on_delivery(self, event):
        if hasattr(event, "message"):
            return
        if self.__message.recv(event.link):
            event.message = self.__message
            dlv = event.delivery
            assert dlv.encoded
            try:
                event.dispatch(event.root, ENCODED_MESSAGE)
                event.dispatch(event.root, MESSAGE)
                dlv.update(Delivery.ACCEPTED)
            except:
                dlv.update(Delivery.REJECTED)
                # XXX: no cause?
                # XXX: no rethrow?
            finally:
                dlv.settle()

