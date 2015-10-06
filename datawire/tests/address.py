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
from unittest import TestCase

class AddressTest(TestCase):

    def testAddressNone(self):
        assert Address(None).host is None
        assert Address(None).port is None

    def testParseNone(self):
        assert Address.parse(None) is None

    def _testParse(self, text, host, port):
        addr = Address.parse(text)
        self.assertEqual(addr.host, host)
        self.assertEqual(addr.port, port)

    def testHost(self):
        # hmm, the port seems to default as an integer, but parse as a
        # string
        self._testParse("//host", "host", "5672")

    def testHostPort(self):
        self._testParse("//host:5673", "host", "5673")

    def testHostPortStuff(self):
        self._testParse("//host:5673/stuff", "host", "5673")

    def testHostStuff(self):
        self._testParse("//host/stuff", "host", "5672")
