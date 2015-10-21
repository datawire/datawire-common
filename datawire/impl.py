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
