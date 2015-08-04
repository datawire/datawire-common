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

from datawire.address import Address

class AddressTest:

    def testAddressNone(self):
        assert Address(None).host is None
        assert Address(None).port is None

    def testParseNone(self):
        assert Address.parse(None) is None

    def _testParse(self, text, host, port):
        addr = Address.parse(text)
        assert addr.host == host, addr.host
        assert addr.port == port, addr.port

    def testHost(self):
        # hmm, the port seems to default as an integer, but parse as a
        # string
        self._testParse("//host", "host", 5672)

    def testHostPort(self):
        self._testParse("//host:5672", "host", "5672")

    def testHostPortStuff(self):
        self._testParse("//host:5672/stuff", "host", "5672")

    def testHostStuff(self):
        self._testParse("//host/stuff", "host", 5672)
