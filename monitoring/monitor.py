# Provides monitoring data to the JS Monitoring UI (or whomever else)

import sys, logging, time, random
from argparse import ArgumentParser

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
        if len(tail) < self.size:
            return tail
        else:
            return tail[len(tail)-self.size:]


class Monitor(object):

    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.tether = Tether(None, "//%s/monitor" % self.host, "//%s:%s" % (self.host, self.port))
        self.stream = Stream(HistoryStore(100))
        self.directory = Receiver("//%s/directory" % self.host, Processor(self))
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
        event.reactor.schedule(1, self)


def main():
    parser = ArgumentParser()
    parser.add_argument("-n", "--host", default="127.0.0.1", help="network hostname")
    parser.add_argument("-p", "--port", default="6000", help="network port")
    args = parser.parse_args()

    Reactor(Monitor(args)).run()


if __name__ == "__main__":
    main()
