'''
Created on 22. jul. 2015

@author: bozzo
'''
import unittest

from datawire.container import ancestors

class AncestorTest(unittest.TestCase):


    def testNone(self):
        self.assertListEqual(
            list(ancestors(None)),
             [None,
              ])

    def testEmpty(self):
        self.assertListEqual(
            list(ancestors("")),
             ["",
              ])

    def testSlash(self):
        self.assertListEqual(
            list(ancestors("/")),
             ["/",
              "",
              ])

    def testPathTwo(self):
        self.assertListEqual(
            list(ancestors("/a/b")),
             ["/a/b",
              "/a/",
              "/a",
              "/",
              "",
              ])

    def testPathTwoSlash(self):
        self.assertListEqual(
            list(ancestors("/a/b/")),
             ["/a/b/",
              "/a/b",
              "/a/",
              "/a",
              "/",
              "",
              ])

    def testEmptyParam(self):
        self.assertListEqual(
            list(ancestors("?a=1")),
             ["",
              ])

    def testSlashParam(self):
        self.assertListEqual(
            list(ancestors("/?a=1")),
             ["/",
              "",
              ])

    def testPathTwoParam(self):
        self.assertListEqual(
            list(ancestors("/a/b?a=1")),
             ["/a/b",
              "/a/",
              "/a",
              "/",
              "",
              ])

    def testPathTwoSlashParam(self):
        self.assertListEqual(
            list(ancestors("/a/b/?a=1")),
             ["/a/b/",
              "/a/b",
              "/a/",
              "/a",
              "/",
              "",
              ])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()