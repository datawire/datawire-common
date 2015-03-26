"""
- Doggy Client (send)
- Theoretically performs auth via the user db
- Allows manual submission of a bark (like ex/send or AutoDoggy)
"""

from argparse import ArgumentParser

from proton.reactor import Reactor
from datawire import Sender

import common


class PutBark(object):

    def __init__(self, message):
        self.message = tuple(message)
        self.sender = Sender("//localhost/outbox/%s" % message.user)

    def on_reactor_init(self, event):
        self.sender.start(event.reactor)
        self.sender.send(self.message)
        self.sender.close()


def main():
    parser = ArgumentParser(prog="bark")
    parser.add_argument("user")
    parser.add_argument("message", nargs="+")
    args = parser.parse_args()

    users = common.load_data("users.pickle")

    assert args.user in users
    content = " ".join(args.message)
    message = common.Message(args.user, content)

    Reactor(PutBark(message)).run()


if __name__ == "__main__":
    main()
