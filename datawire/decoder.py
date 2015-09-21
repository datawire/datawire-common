# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

import sys, traceback
from proton import EventType, Message, Delivery

from .impl import dual_impl, DatawireEvent

ENCODED_MESSAGE = EventType("encoded_message", DatawireEvent.Type.ENCODED_MESSAGE)
MESSAGE = EventType("message", DatawireEvent.Type.MESSAGE)

@dual_impl
class Decoder:

    def __init__(self, delegate=None):
        if delegate is None:
            self.__delegate = self
        else:
            self.__delegate = delegate
        self.__message = Message()

    def on_delivery(self, event):
        if self.__message.recv(event.link):
            event.message = self.__message
            dlv = event.delivery
            assert dlv.encoded
            try:
                event.dispatch(self.__delegate, ENCODED_MESSAGE)
                event.dispatch(self.__delegate, MESSAGE)
                dlv.update(Delivery.ACCEPTED)
            except:
                dlv.update(Delivery.REJECTED)
                traceback.print_exc()
                print sys.exc_info()
                # TODO no rethrow?
            finally:
                dlv.settle()
