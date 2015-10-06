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
