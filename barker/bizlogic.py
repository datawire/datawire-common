# Bizlogic

"""
  - Receives barks (//host/bizlogic)
  - Rereads user and hashtag database periodically
  - Pushes to relevant users inboxes (//host/inbox/user)
"""

from proton.reactor import Reactor
from datawire import Sender, Tether, Processor

import common

class BizLogic(object):

    def __init__(self):
        self.host = "localhost"
        self.port = 5680
        self.tether = Tether(None, "//%s/bizlogic" % self.host, "//%s:%s" % (self.host, self.port))

        self.users = {}
        self.user_reread_period = 30  # seconds

    def on_reactor_init(self, event):
        event.reactor.acceptor(self.host, self.port, Processor(self))
        self.tether.start(event.reactor)
        event.reactor.schedule(0, self)

    def on_timer_task(self, event):
        self.users = common.load_data("users.pickle")
        event.reactor.schedule(self.user_reread_period, self)

    def on_message(self, event):
        message = common.Message(*event.message.body)
        words = message.content.split()
        mentions = [word[1:] for word in words if word.startswith("@")]
        user = self.users[message.user]
        followers = user.getFollowers(self.users)
        targets = set(mentions + followers)
        for target in targets:
            sender = Sender("//localhost/inbox/%s" % target)
            sender.start(event.reactor)
            sender.send(event.message.body)
            sender.close()


def main():
    Reactor(BizLogic()).run()

if __name__ == "__main__":
    main()
