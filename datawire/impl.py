# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

__all__ = ["dual_impl", "DatawireEvent"]
import platform
if platform.python_implementation() == 'Jython':
  from jdatawire import dual_impl, DatawireEvent
else:
  def dual_impl(clazz=None, **kwargs):
    def wrap(klazz):
      return klazz
    if clazz is None:
      return wrap
    else:
      return wrap(clazz)
  dual_impl.dualImpls = set()
  class DatawireEvent:
    class Type:
      ENCODED_MESSAGE = None
      MESSAGE = None
      SAMPLE = None
      DRAINED = None
