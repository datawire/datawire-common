# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from unittest import TestCase
from proton import Message
from proton.reactor import Reactor
from datawire import Store, Entry

from .common import *

class StoreTest(TestCase):
  
  def setUp(self):
    self.store = Store()

  def testEmpty(self):
    r = self.store.reader()
    self.assertFalse(r.more(), "Empty store should be empty")

  def testPlain(self):
    self.store.put("hello")
    r = self.store.reader()
    self.assertTrue(r.more(), "Store should not be empty")
    e = r.next()
    self.assertFalse(r.more(), "Store should be empty")
    self.assertEqual("hello", str(e.message))
  def testGc(self):
    map(self.store.put, "A B C D E F".split())
    r = self.store.reader()
    r.next()
    r.next()
    r.next()
    self.store.gc()

class DerivedStore(Store):
  def __init__(self, name=None):
    Store.__init__(self, name)

class DerivedStoreTest(StoreTest):

  def setUp(self):
    self.store = DerivedStore()