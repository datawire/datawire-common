import os, signal
from argparse import ArgumentParser
from subprocess import Popen
from time import sleep

import common

commands = """
directory --host %(hostname)s
manifold //%(hostname)s/inbox --port 5820 --history 25
python bizlogic.py --host %(hostname)s --port 5680
#python bizlogic.py --host %(hostname)s --port 5681
#python bizlogic.py --host %(hostname)s --port 5682
manifold //%(hostname)s/outbox --port 5800 --push //%(hostname)s/bizlogic
manifold //%(hostname)s/outbox --port 5801 --push //%(hostname)s/bizlogic
manifold //%(hostname)s/outbox --port 5802 --push //%(hostname)s/bizlogic
python autobark.py 5 --host %(hostname)s
python autobark.py 5 --host %(hostname)s
python autobark.py 5 --host %(hostname)s
python autobark.py 5 --host %(hostname)s
python autobark.py 5 --host %(hostname)s
python listen.py ark3 --host %(hostname)s
%(webui_proxy)s --thost %(hostname)s -p 5673 -t 5820
%(webui_proxy)s --thost %(hostname)s -p 5674 -t 5800
"""

def launch(command):
    try:
        pid = Popen(command.split()).pid
    except OSError as exc:
        print "Failed to launch %r" % command
        print " (%s)" % exc
        print "Are your shell PATH and PYTHONPATH variables set for Datawire?"
        exit(1)
    print "[%5d] %s" % (pid, command)
    sleep(0.3)
    return pid

def main():
    parser = ArgumentParser()
    parser.add_argument("-n", "--host", default="127.0.0.1", help="network hostname")
    parser.add_argument("--webui-only", default=False, action="store_true", help="start only webui helpers")
    parser.add_argument("--webui-proxy", default="webui/proxy/proxy.js", help="location of the proxy")
    args = parser.parse_args()

    params = dict(hostname=args.host,
                  webui_proxy=args.webui_proxy)

    try:
        open("users.pickle")
    except IOError:
        common.make_users("users.pickle", 100)

    with open("webui/barker_host.js", "wb") as jsfile:
        jsfile.write("""barker_host = "%(hostname)s";\n""" % params)

    pids = []
    try:
        for command in (commands % params).split("\n"):
            if command and not command.strip().startswith("#") and (command.strip().startswith(args.webui_proxy) or not args.webui_only):
                pids.append(launch(command.strip()))
        while True:
            sleep(100000)
    finally:
        for pid in pids:
            os.kill(pid, signal.SIGTERM)


if __name__ == "__main__":
    main()
