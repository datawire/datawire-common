# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

import os, sys, time
try:
    import resource
except:
    class resource:
        RUSAGE_SELF = object()
        @staticmethod
        def getrusage(what):
            return object()

from proton import Message, timestamp
from proton.handlers import CHandshaker
from .counts import lib
from .sampler import Sampler
from datawire.stats import app, lib

class SlidingRate:

    def __init__(self, period = 10):
        self.period = period
        self.samples = [(0, 0.0)]*self.period

    def rate(self, count, tstamp):
        self.samples.pop(0)
        self.samples.append((count, tstamp))
        fcount, ftime = self.samples[0]
        return (count - fcount)/(tstamp - ftime)

class Agent:

    def __init__(self, tether, delegate=None):
        self.tether = tether
        if delegate is None:
            self.__delegate = self
        else:
            self.__delegate = delegate
        self.pid = os.getpid()
        self.incoming = SlidingRate()
        self.outgoing = SlidingRate()
        self.incoming_lib = SlidingRate()
        self.outgoing_lib = SlidingRate()
        self.sampler = Sampler(self)
        self.message = Message()
        self.handlers = [CHandshaker(), self.sampler]

    def on_link_local_open(self, event):
        event.link.counts = lib

    def stats(self):
        tstamp = time.time()
        rusage = {}
        ru = resource.getrusage(resource.RUSAGE_SELF)
        for attr in (u'ru_idrss', u'ru_inblock', u'ru_isrss', u'ru_ixrss',
                     u'ru_majflt', u'ru_maxrss', u'ru_minflt', u'ru_msgrcv',
                     u'ru_msgsnd', u'ru_nivcsw', u'ru_nsignals', u'ru_nswap',
                     u'ru_nvcsw', u'ru_oublock', u'ru_stime', u'ru_utime'):
            if hasattr(ru, attr):
                rusage[attr] = getattr(ru, attr)
        result = {u"address": self.tether.address,
                  u"agent": self.tether.agent,
                  u"type": self.tether.agent_type,
                  u"timestamp": timestamp(tstamp*1000),
                  u"pid": self.pid,
                  u"rusage": rusage,
                  u"times": os.times(),
                  u"command": map(unicode, [sys.executable] + sys.argv),
                  u"incoming_count": app.incoming,
                  u"outgoing_count": app.outgoing,
                  u"incoming_count_lib": lib.incoming,
                  u"outgoing_count_lib": lib.outgoing,
                  u"incoming_rate": self.incoming.rate(app.incoming, tstamp),
                  u"outgoing_rate": self.outgoing.rate(app.outgoing, tstamp),
                  u"incoming_rate_lib": self.incoming_lib.rate(lib.incoming, tstamp),
                  u"outgoing_rate_lib": self.outgoing_lib.rate(lib.outgoing, tstamp)}
        return result

    def on_sample(self, event):
        stats = self.stats()
        self.__delegate.sample(stats)
        self.message.body = stats
        event.link.send(self.message).settle()

    def sample(self, stats):
        pass
