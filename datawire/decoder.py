# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

import sys, traceback
from proton import EventType, Message, Delivery

MESSAGE = EventType("message")

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
            try:
                event.dispatch(self.__delegate, MESSAGE)
                dlv.update(Delivery.ACCEPTED)
            except:
                dlv.update(Delivery.REJECTED)
                traceback.print_exc()
                print sys.exc_info()
            finally:
                dlv.settle()
