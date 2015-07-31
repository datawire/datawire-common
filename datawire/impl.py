# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

__all__ = ["dualImpls", "dual_impl", "DatawireEvent"]
dualImpls = set()
try:
  from jdatawire import impls
  from jdatawire import io_datawire_DatawireEvent as DatawireEvent
  def dual_impl(clazz):
    if hasattr(impls, clazz.__name__):
      if clazz.__name__ not in dualImpls:
        dualImpls.add(clazz.__name__)
      return getattr(impls, clazz.__name__)
    else:
      return clazz
except:
  def dual_impl(clazz):
    return clazz
  class DatawireEvent:
    class Type:
      MESSAGE = None
      SAMPLE = None
      DRAINED = None
