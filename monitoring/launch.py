import os, signal
from argparse import ArgumentParser
from subprocess import Popen
from time import sleep

commands = """
python monitor.py --host %(hostname)s
../barker/webui/proxy/proxy.js --thost %(hostname)s -p 5700 -t 6000
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
    args = parser.parse_args()

    params = dict(hostname=args.host)

    with open("monitor_host.js", "wb") as jsfile:
        jsfile.write("""monitor_host = "%(hostname)s";\n""" % params)

    pids = []
    try:
        for command in (commands % params).split("\n"):
            if command and not command.strip().startswith("#"):
                pids.append(launch(command.strip()))
        while True:
            sleep(100000)
    finally:
        for pid in pids:
            os.kill(pid, signal.SIGTERM)


if __name__ == "__main__":
    main()
