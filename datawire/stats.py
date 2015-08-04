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

import proton

from .counts import app, lib

ProtonSender = proton.Sender
ProtonReceiver = proton.Receiver

class Sender(proton.Sender):

    def send(self, *args, **kwargs):
        getattr(self, "counts", app).outgoing += 1
        return ProtonSender.send(self, *args, **kwargs)

class Receiver(proton.Receiver):

    def recv(self, *args, **kwargs):
        getattr(self, "counts", app).incoming += 1
        return ProtonReceiver.recv(self, *args, **kwargs)

proton.Sender = Sender
proton.Receiver = Receiver
