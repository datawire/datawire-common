# Submission

"""
  - Service that receives "outgoing" barks (//host/outbox)
  - Has a stream for each user that pushes to bizlogic
"""

from proton.reactor import Reactor
from datawire import Tether, Sender, Stream

class Submission(object):

    def __init__(self):
        self.host = "localhost"
        self.port = 5679
        self.tether = Tether(None, "//%s/outbox" % self.host, "//%s:%s" % (self.host, self.port))
        self.stream = Stream()
        self.sender = Sender("//localhost/bizlogic", self.stream)
        self.handlers = [self.stream]  # WTF does this really do?

    def on_reactor_init(self, event):
        event.reactor.acceptor(self.host, self.port, self.stream)
        self.tether.start(event.reactor)
        self.sender.start(event.reactor)


def main():
    Reactor(Submission()).run()

if __name__ == "__main__":
    main()
