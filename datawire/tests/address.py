# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

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
        self._testParse("//host", "host", 5672)

    def testHostPort(self):
        self._testParse("//host:5672", "host", "5672")

    def testHostPortStuff(self):
        self._testParse("//host:5672/stuff", "host", "5672")

    def testHostStuff(self):
        self._testParse("//host/stuff", "host", 5672)
