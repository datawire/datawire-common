# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

dualImpls = set()
try:
  import jdatawire
  def dual_impl(clazz):
    if hasattr(jdatawire, clazz.__name__):
      dualImpls.add(clazz.__name__)
      return getattr(jdatawire, clazz.__name__)
    else:
      return clazz
  Event = jdatawire.Event
except:
  def dual_impl(clazz):
    return clazz
  class Event:
    class Type:
      MESSAGE = None
