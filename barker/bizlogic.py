# Bizlogic

"""
  - Receives barks (//host/bizlogic)
  - Rereads user and hashtag database periodically
  - Pushes to relevant users inboxes (//host/inbox/user)
"""

from proton.reactor import Reactor
from datawire import Agent, Container, Linker, Sender, Tether, Processor

import common

class BizLogic(object):

    def __init__(self):
        self.host = "localhost"
        self.port = 5680
        self.tether = Tether(None, "//%s/bizlogic" % self.host, None,
                             host=self.host, port=self.port, agent_type="bizlogic")

        self.users = {}
        self.user_reread_period = 30  # seconds
        self.linker = Linker()
        self.container = Container(Processor(self))
        self.container[self.tether.agent] = Agent(self.tether)
        self.handlers = [self.container]

    def on_reactor_init(self, event):
        event.reactor.acceptor(self.host, self.port)
        self.tether.start(event.reactor)
        event.reactor.schedule(0, self)
        self.linker.start(event.reactor)

    def on_timer_task(self, event):
        self.users = common.load_data("users.pickle")
        event.reactor.schedule(self.user_reread_period, self)

    def on_message(self, event):
        message = common.Message(*event.message.body)
        words = message.content.split()
        mentions = [word[1:] for word in words if word.startswith("@")]
        user = self.users[message.user]
        followers = user.getFollowers(self.users)
        targets = set(mentions + followers + [message.user])
        for target in targets:
            sender = self.linker.sender("//localhost/inbox/%s" % target)
            sender.send(event.message.body)


def main():
    Reactor(BizLogic()).run()

if __name__ == "__main__":
    main()
