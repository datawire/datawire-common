# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

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

