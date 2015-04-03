# Central storage for Doggy

import cPickle, os, sys, random, time, logging
from collections import namedtuple

logging.basicConfig(level=logging.INFO, datefmt="%H%M%S",
                    format="%(asctime)s " + sys.argv[0].replace(".py", "") + " %(name)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

def dump_data(filename, data):
    tempname = filename + ".temp"
    with open(tempname, "wb") as outf:
        cPickle.dump(data, outf)
    os.rename(tempname, filename)

def load_data(filename):
    with open(filename) as inf:
        return cPickle.load(inf)


class User(object):
    def __init__(self, name):
        self.name = name
        self.follows = []
        self.autobark = True

    def getFollowers(self, users):
        return [other.name for other in users.viewvalues() if self.name in other.follows]

def make_users(filename, count):
    # http://dogtime.com/top-100-dog-names.html
    hardcoded = "ark3 rdl rhs".split()
    names = """Bailey Max Charlie Buddy Rocky Jake Jack Toby Cody Buster Duke
            Cooper Riley Harley Bear Tucker Murphy Lucky Oliver Sam Oscar Teddy
            Winston Sammy Rusty Shadow Gizmo Bentley Zeus Jackson Baxter Bandit
            Gus Samson Milo Rudy Louie Hunter Casey Rocco Sparky Joey Bruno
            Beau Dakota Maximus Romeo Boomer Luke Henry Bella Lucy Molly Daisy
            Maggie Sophie Sadie Chloe Bailey Lola Zoe Abby Ginger Roxy Gracie
            Coco Sasha Lily Angel Princess Emma Annie Rosie Ruby Lady Missy
            Lilly Mia Katie Zoey Madison Stella Penny Belle Casey Samantha
            Holly Lexi Lulu Brandy Jasmine Shelby Sandy Roxie Pepper Heidi Luna
            Dixie Honey Dakota""".split()
    usernames = ["%s-%06x" % (random.choice(names), idx) for idx in range(count)]
    usernames.extend(hardcoded)
    users = {username: User(username) for username in usernames}
    for username in usernames:
        follows = set(random.sample(usernames, min(len(usernames) / 2,
                                                   int(10 ** (random.random() * 3)))))  # Follow at most 10**3 users
        follows.update(random.sample(hardcoded, 2))  # But always follow at least two of us
        users[username].follows = list(follows)
    for username in hardcoded:
        users[username].autobark = False
    dump_data(filename, users)


_Message = namedtuple("Message", "user content id")
def Message(user, content, id=None):
    if id is None:
        id = "msg%04x%010x" % (os.getpid(), time.time() * 100)
    return _Message(user, content, id)
