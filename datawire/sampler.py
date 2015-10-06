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

from proton import EventType, PN_LOCAL_ACTIVE

from .impl import dual_impl, DatawireEvent

SAMPLE = EventType("sample", DatawireEvent.Type.SAMPLE)

@dual_impl
class Sampler:

    def __init__(self, delegate=None, frequency=1):
        if delegate is None:
            self.__delegate = self
        else:
            self.__delegate = delegate
        self.frequency = frequency

    def on_link_local_open(self, event):
        self._sample(event)

    def _sample(self, event):
        link = event.link
        if link and link.state & PN_LOCAL_ACTIVE:
            event.dispatch(self.__delegate, SAMPLE)
            event = event.copy()
            class Sample:
                def on_timer_task(_self, _):
                    self._sample(event)
            event.reactor.schedule(1.0/self.frequency, Sample()) # FIXME: schedule is in milliseconds ?
