# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

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
