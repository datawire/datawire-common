# Distribution

"""
  - Service that receives "incoming" barks (//host/inbox)
  - Has a stream for each user that keeps up to 20 barks handy
"""

from argparse import ArgumentParser

from proton.reactor import Reactor
from datawire import Tether, Stream

class Distribution(object):

    def __init__(self, user=None):
        self.host = "localhost"
        self.port = 5681
        if user:
            address = "//%s/inbox/%s" % (self.host, user)
            self.port += sum(ord(ch) for ch in user)
        else:
            address = "//%s/inbox" % self.host
        self.tether = Tether(None, address, "//%s:%s" % (self.host, self.port))
        self.stream = Stream()
        self.handlers = [self.stream]  # WTF does this really do?

    def on_reactor_init(self, event):
        event.reactor.acceptor(self.host, self.port, self.stream)
        self.tether.start(event.reactor)


def main():
    parser = ArgumentParser()
    parser.add_argument("-u", "--user", help="collect for this user")
    args = parser.parse_args()

    Reactor(Distribution(args.user)).run()

if __name__ == "__main__":
    main()
