from argparse import ArgumentParser

from proton.reactor import Reactor
from datawire import Sender

import common


class PutBark(object):

    def __init__(self, user, content, hostname):
        self.bark = common.Bark(user, content)
        self.sender = Sender("//%s/outbox/%s" % (hostname, user))

    def on_reactor_init(self, event):
        self.sender.start(event.reactor)
        self.sender.send(tuple(self.bark))
        self.sender.close()


def main():
    parser = ArgumentParser(prog="bark")
    parser.add_argument("user")
    parser.add_argument("content", nargs="+")
    parser.add_argument("-n", "--host", default="127.0.0.1", help="hostname of outboxes")
    args = parser.parse_args()
    users = common.load_data("users.pickle")

    assert args.user in users
    content = " ".join(args.content)

    Reactor(PutBark(args.user, content, args.host)).run()


if __name__ == "__main__":
    main()
