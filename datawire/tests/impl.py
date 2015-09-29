# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.
import datawire
from unittest import TestCase
from warnings import warn
from datawire.impl import dual_impl

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
    except ImportError:
      import platform
      imp = platform.python_implementation()
      self.assertNotEquals(imp, "Jython")
      self.skipTest("Not a Jython run, platform=" + imp)

  def testDualImplCoverage(self):
    self.checkRunningOnJython()
    datawireImpls = set(n for n in dir(datawire) if n[:1].isupper())
    pythonImpls = datawireImpls - dual_impl.dualImpls
    def clazzof(impls):
      return (getattr(datawire, name) for name in impls)
    for clazz in clazzof(dual_impl.dualImpls):
      self.assertIsJavaImpl(clazz)
    for clazz in clazzof(pythonImpls):
      self.assertIsPythonImpl(clazz)
