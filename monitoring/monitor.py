# Provides monitoring data to the JS Monitoring UI (or whomever else)

import sys, logging, time, random

from proton import timestamp
from proton.reactor import Reactor
from datawire import Tether, Stream, Processor, Receiver
from datawire.stream import Store

logging.basicConfig(level=logging.INFO, datefmt="%H%M%S",
                    format="%(asctime)s " + sys.argv[0].replace(".py", "") + " %(name)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# Copy-pasta!
class HistoryStore(Store):

    def __init__(self, size=0):
        Store.__init__(self)
        self.size = size

    def compact(self, tail):
        return tail[len(tail)-self.size:]


class Monitor(object):

    def __init__(self):
        self.host = "localhost"
        self.port = 6000
        self.tether = Tether(None, "//localhost/monitor", "//%s:%s" % (self.host, self.port))
        self.stream = Stream(HistoryStore(100))
        self.directory = Receiver("//localhost/directory", Processor(self))
        self.receivers = []
        self.handlers = [self.stream]
        self.statMessages = []

    def on_reactor_init(self, event):
        event.reactor.acceptor(self.host, self.port, self.stream)
        self.tether.start(event.reactor)
        self.directory.start(event.reactor)
        event.reactor.schedule(0, self)

    def add_routes(self, event):
        address, routes = event.message.body
        if "/agents/" in address:
            if routes:
                rcv = Receiver(address, Processor(self))
                self.receivers.append(rcv)
                rcv.start(event.reactor)
            else:
                for rcv in self.receivers:
                    if rcv.source == address:
                        self.receivers.remove(rcv)
                        rcv.stop(event.reactor)
                        break

    def on_message(self, event):
        if event.message.subject == "routes":
            self.add_routes(event)
        else:
            self.statMessages.append(event.message.body)

    def on_timer_task(self, event):
        if self.statMessages:
            self.stream.put(self.statMessages)
            self.statMessages = []
        event.reactor.schedule(0.25, self)

    def old_on_timer_task(self, event):
        now = timestamp(time.time() * 1000)
        addresses = [u"bizlogic"] + 10 * [u"inbox"] + 5 * [u"outbox"]
        sources = [(u"//localhost/" + address, u"//localhost/agents/localhost-%d" % (5000+idx))
                   for idx, address in enumerate(addresses)]

        random.shuffle(sources)
        stat_names_summed = u"manifold_messages manifold_streams".split()
        stat_names_averaged = u"manifold_last_idle incoming_rate outgoing_rate".split()
        stat_names = stat_names_summed + stat_names_averaged

        message = []
        aggCounts = {u"inbox": 0, u"outbox": 0}
        for address, agent in sources:
            content = {
                u"timestamp": now,
                u"address": address,
                u"agent": agent
            }
            for stat_name in stat_names:
                content[stat_name] = random.random() * 100
            message.append(content)
            for name in aggCounts:
                if name in address:
                    aggCounts[name] += 1
                    break

        aggContents = {key: {} for key in aggCounts}
        for content in message:
            for name in aggContents:
                if name in content[u"address"]:
                    aggContent = aggContents[name]
                    if not aggContent:
                        aggContent.update(content)
                        aggContent[u"agent"] = u"all"
                    else:
                        for stat_name in stat_names:
                            aggContent[stat_name] += content[stat_name]

        for name, aggContent in aggContents.items():
            for stat_name in stat_names_averaged:
                aggContent[stat_name] /= aggCounts[name]
            message.append(aggContent)


        self.stream.put(message)
        event.reactor.schedule(1, self)


def main():
    Reactor(Monitor()).run()


if __name__ == "__main__":
    main()
