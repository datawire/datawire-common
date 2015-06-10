import logging, datetime
from argparse import ArgumentParser

from proton.reactor import Reactor
from datawire import Receiver, Processor

import common
log = logging.getLogger(__name__)

class GetBarks(object):

    def __init__(self, user, hostname):
        self.user = user
        self.receiver = Receiver("//%s/inbox/%s" % (hostname, user), Processor(self))
        self.width = 10

    def on_reactor_init(self, event):
        self.receiver.start(event.reactor)

    def on_message(self, event):
        bark = common.Bark(*event.message.body)
        self.width = max(self.width, len(bark.user))
        print datetime.datetime.now().strftime("%H:%M:%S"), \
              self.user, "<--", "%%%ds:" % self.width % bark.user, \
              bark.content

def main():
    parser = ArgumentParser(prog="listen")
    parser.add_argument("user")
    parser.add_argument("-n", "--host", default="127.0.0.1", help="hostname of inboxes")
    args = parser.parse_args()

    users = common.load_data("users.pickle")

    assert args.user in users
    Reactor(GetBarks(args.user, args.host)).run()


if __name__ == "__main__":
    main()
