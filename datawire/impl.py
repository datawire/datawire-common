# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

__all__ = ["dual_impl", "DatawireEvent"]
try:
  from jdatawire import dual_impl, DatawireEvent
except:
  import traceback
  traceback.print_exc(None, None)
  def dual_impl(clazz):
    return clazz
  dual_impl.dualImpls = set()
  class DatawireEvent:
    class Type:
      ENCODED_MESSAGE = None
      MESSAGE = None
      SAMPLE = None
      DRAINED = None
