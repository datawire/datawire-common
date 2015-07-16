# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.
import datawire
from unittest import TestCase
from warnings import warn
from datawire.impl import dualImpls

class ImplTest(TestCase):

  def assertIsJavaImpl(self, clazz):
    self.assertRegexpMatches(clazz.__module__, "^(io.datawire|jdatawire)", "Expected %s.%s to be a Java impl" % (clazz.__module__, clazz.__name__))

  def assertIsPythonImpl(self, clazz):
    name = "%s.%s" % (clazz.__module__, clazz.__name__)
    warn("Missing Java implementation of class %s" % name, stacklevel=2)
    self.assertRegexpMatches(clazz.__module__, "^(datawire)", "Expected %s to be a datawire Python impl" % name)

  def checkRunningOnJython(self):
    try:
      import jdatawire
    except:
      import sys, traceback
      traceback.print_exc()
      self.assertNotEquals(sys.platform, "jython")
      self.skipTest("Not a jython run, platform=" + sys.platform)

  def testDualImplCoverage(self):
    self.checkRunningOnJython()
    datawireImpls = set(n for n in dir(datawire) if n[:1].isupper())
    pythonImpls = datawireImpls - dualImpls
    def clazzof(impls):
      return (getattr(datawire, name) for name in impls)
    for clazz in clazzof(dualImpls):
      self.assertIsJavaImpl(clazz)
    for clazz in clazzof(pythonImpls):
      self.assertIsPythonImpl(clazz)
