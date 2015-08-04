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
