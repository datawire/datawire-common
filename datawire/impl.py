# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

__all__ = ["dualImpls", "dual_impl", "Event"]
dualImpls = set()
try:
  from jdatawire import impls, Event
  def dual_impl(clazz):
    if hasattr(impls, clazz.__name__):
      dualImpls.add(clazz.__name__)
      return getattr(impls, clazz.__name__)
    else:
      return clazz
except:
  def dual_impl(clazz):
    return clazz
  class Event:
    class Type:
      MESSAGE = None
      SAMPLE = None
      DRAINED = None
