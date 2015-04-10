import os, signal
from subprocess import Popen
from time import sleep

commands = """
python monitor.py
../barker/webui/proxy/proxy.js --thost localhost -p 5700 -t 6000
"""

def launch(command):
    pid = Popen(command.split()).pid
    print "[%5d] %s" % (pid, command)
    sleep(0.3)
    return pid

def main():
    pids = []
    try:
        for command in commands.split("\n"):
            if command and not command.strip().startswith("#"):
                pids.append(launch(command.strip()))
        sleep(100000)
    finally:
        for pid in pids:
            os.kill(pid, signal.SIGTERM)


if __name__ == "__main__":
    main()
