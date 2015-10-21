'''
Created on 22. jul. 2015

@author: bozzo
'''
import unittest

from datawire.container import ancestors

class AncestorTest(unittest.TestCase):
    longMessage = True # force list diff output

    expected = {
                "" : [""],
                "/" : ["/", ""],
                "/a" : ["/a", "/", ""],
                "/a/" : ["/a/", "/a", "/", ""],
                "/a/b" : ["/a/b", "/a/", "/a", "/", ""],
                "/a/b/" : ["/a/b/", "/a/b", "/a/", "/a", "/", ""],
                }

    def checkAncestor(self, path, expected):
        self.assertListEqual(list(ancestors(path)), self.expected[expected], "\n while checking the ancestors of path %s" % repr(path))

    def checkExpectedVariants(self, prefix = "", postfix = ""):
        for expected in self.expected:
            path = prefix + expected + postfix
            self.checkAncestor(path, expected)

    def testNone(self):
        self.assertListEqual(list(ancestors(None)), [None,])

    def testPath(self):
        self.checkExpectedVariants()

    def testPathParam(self):
        self.checkExpectedVariants(postfix = "?param=/value")

    def testHostPath(self):
        self.checkExpectedVariants(prefix = "//host:12234")

    def testHostPathParam(self):
        self.checkExpectedVariants(prefix = "//host:12234", postfix="?param=/value")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()