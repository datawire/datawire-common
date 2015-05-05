"""
  - Like ex/send, but runs forever. Run as many of these as we want.
  - Rereads user and hashtag database periodically
  - Generates random barks on a timer, say 5-10 barks every second
    - Chooses a random user that allows auto-barking
    - Some chance of mentioning a hashtag, based on hashtag probabilities in db
    - Some chance of mentioning a user, based on how many users follow that user
  - Pushes barks to submission (//host/outbox/user)
"""

import time, random
from argparse import ArgumentParser

from proton.reactor import Reactor
from datawire import Linker

import common

class AutoBark(object):

    def __init__(self, rate, hostname):
        self.users = {}
        try:
            self.quotes = open("quotes.txt").read().split("\n")
        except IOError:
            self.quotes = [
            """"On the Internet, everybody knows you're a dog." --Oscar Wilde"""
            ]
        self.last_user_reread = 0
        self.user_reread_period = 30  # seconds
        self.bark_period = 1.0 / rate  # seconds
        self.linker = Linker()
        self.hostname = hostname

    def make_random_bark(self):
        while True:
            username = random.choice(self.users.keys())
            user = self.users[username]
            if user.autobark:
                break
        if random.random() > 0.9:
            messageText = random.choice(self.quotes)
        else:
            words = [random.choice(["woof", "arf", "ruff", "yap"]) for idx in range(random.randint(3, 8))]
            if random.random() > 0.75:
                words.append("@" + random.choice(user.follows))  # one can always dream
            if random.random() > 0.9:
                words.append("#subwoofer")
            messageText = " ".join(words)
        return common.Message(username, messageText)

    def on_reactor_init(self, event):
        event.reactor.schedule(0, self)
        self.linker.start(event.reactor)

    def on_timer_task(self, event):
        now = time.time()
        if now - self.last_user_reread > self.user_reread_period:
            self.users = common.load_data("users.pickle")
            self.last_user_reread = now

        message = self.make_random_bark()
        sender = self.linker.sender("//%s/outbox/%s" % (self.hostname, message.user))
        sender.send(tuple(message))

        event.reactor.schedule(self.bark_period, self)


def main():
    parser = ArgumentParser()
    parser.add_argument("rate", type=float, help="Message per second")
    parser.add_argument("-n", "--host", default="localhost", help="hostname of outboxes")
    args = parser.parse_args()

    Reactor(AutoBark(args.rate, args.host)).run()

if __name__ == "__main__":
    main()
