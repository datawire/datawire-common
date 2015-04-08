# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from proton import EventType, PN_LOCAL_ACTIVE

SAMPLE = EventType("sample")

class Sampler:

    def __init__(self, delegate=None, frequency=10):
        if delegate is None:
            self.__delegate = self
        else:
            self.__delegate = delegate
        self.frequency = frequency

    def on_link_local_open(self, event):
        self._sample(event)

    def _sample(self, event):
        link = event.link
        if link.state & PN_LOCAL_ACTIVE:
            event.dispatch(self.__delegate, SAMPLE)
            class Sample:
                def on_timer_task(_self, _):
                    self._sample(event)
            event.reactor.schedule(1.0/self.frequency, Sample())
