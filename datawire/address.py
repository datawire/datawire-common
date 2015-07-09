# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from .impl import dual_impl

def _network(address):
    if address is None: return None
    if address.startswith("//"):
        return address[2:].split("/", 1)[0]
    else:
        return None

def _hostport(network):
    if network is None: return None, None
    if ":" in network:
        return network.split(":", 1)
    else:
        return network, 5672

@dual_impl
class Address:

    @staticmethod
    def parse(text):
        if text is None:
            return None
        else:
            return Address(text)

    def __init__(self, text):
        self.text = text
        self.network = _network(text)
        self.host, self.port = _hostport(self.network)

    def __str__(self):
        return self.text
