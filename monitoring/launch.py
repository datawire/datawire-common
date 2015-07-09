import os, signal
from argparse import ArgumentParser
from subprocess import Popen
from time import sleep

commands = """
python monitor.py --host %(hostname)s
%(webui_proxy)s --thost %(hostname)s -p 5700 -t 6000
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
    parser.add_argument("--webui-proxy", default="../barker/webui/proxy/proxy.js", help="location of the proxy")
    args = parser.parse_args()

    params = dict(hostname=args.host,
                  webui_proxy=args.webui_proxy)

    with open("monitor_host.js", "wb") as jsfile:
        jsfile.write("""monitor_host = "%(hostname)s";\n""" % params)

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
