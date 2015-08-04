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
