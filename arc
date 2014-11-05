#!/usr/bin/env python

import curses, time, sys
from curses import ascii
from common import *

try:
    import dbus
    bus = dbus.SessionBus()
    notifications = dbus.Interface(bus.get_object("org.freedesktop.Notifications",
                                                  "/org/freedesktop/Notifications"),
                                   "org.freedesktop.Notifications")
except ImportError:
    notifications = None

if notifications is None:
    if sys.platform == "darwin":
        def notify(title, msg):
            t = '-title {!r}'.format("arc")
            s = '-subtitle {!r}'.format(title)
            m = '-message {!r}'.format(msg)
            os.system('terminal-notifier {}'.format(' '.join([m, t, s])))
    else:
        def notify(pfx, msg):
            pass
else:
    def notify(title, msg):
        app_name     = "arc"
        replace_id   = 1
        icon         = ""
        title        = title
        text         = msg
        actions_list = ''
        hint         = ''
        time         = 5000   # Use seconds x 1000
        notifications.Notify(app_name, replace_id, icon, title, text, actions_list, hint, time)

class Client(Handler):

    def __init__(self, win, send_address, recv_address, notify=False):
        self.offset = 0
        self.lines = []
        self.input = ""
        self.win = win
        self.sendq = SendQueue(send_address)
        self.recvq = RecvQueue(recv_address, self)
        self.decoder = MessageDecoder(self)
        self.exiting = False
        self.notify = notify

        if self.sendq.address.host == self.recvq.address.host:
            self.send_name = self.sendq.address.path
            self.recv_name = self.recvq.address.path
        else:
            self.send_name = str(self.sendq.address)
            self.recv_name = str(self.recvq.address)

    def fileno(self):
        return 0

    def reading(self):
        return True

    def writing(self):
        return False

    def tick(self, now):
        pass

    def closed(self):
        return self.exiting

    def on_start(self, drv):
        self.driver = drv
        self.driver.add(self)
        self.decoder.on_start(drv)
        self.sendq.on_start(drv)
        self.recvq.on_start(drv)
        self.render()

    def pp(self, msg):
        if not msg.properties:
            return str(msg.body)
        else:
            return str(msg)

    def abbreviate(self, address):
        addr = Address(address)
        if addr.host == self.recvq.address.host and \
           addr.host == self.sendq.address.host:
            return addr.path
        else:
            return address

    def on_message(self, rcv, msg):
        pretty = self.pp(msg)
        name = self.abbreviate(msg.reply_to or rcv.source.address or "")

        if msg.creation_time:
            prefix = "%s <- %s" % (time.ctime(msg.creation_time), name)
        else:
            prefix = "<- %s" % name

        self.lines.append("%s %s" % (prefix, pretty))
        self.render()
        if self.notify:
            notify(name, pretty)

    def readable(self):
        c = self.win.getch()
        if c == 10:
            msg = Message()
            msg.creation_time = time.time()
            msg.reply_to = str(self.recvq.address)
            msg.body = unicode(self.input)
            self.sendq.put(msg)
            self.lines.append("%s %s -> %s" % (time.ctime(msg.creation_time), self.recv_name, self.input))
            self.input = ""
        elif c in (curses.KEY_BACKSPACE, curses.KEY_DC):
            if self.input:
                self.input = self.input[:-1]
        elif c == curses.KEY_UP:
            self.offset += 1
        elif c == curses.KEY_DOWN:
            if self.offset > 0:
                self.offset -= 1
        elif c == 4:
            self.exiting = True
            self.sendq.conn.close()
            self.recvq.conn.close()
            self.driver.exit()
        elif ascii.isprint(c):
            self.input = "%s%c" % (self.input, c)
        else:
            self.input = "%s<%s>" % (self.input, c)
        self.render()

    def render(self):
        self.win.clear()
        h, w = self.win.getmaxyx()
        if self.offset:
            lines = self.lines[-(h-2)-self.offset:-self.offset]
        else:
            lines = self.lines[-(h-2):]
        y = h - len(lines) - 2
        for l in lines:
            self.win.addstr(y, 0, l)
            y += 1
        self.win.hline(y, 0, "=", w)
        self.win.addstr(y + 1, 0, self.input)
        self.win.refresh()

def main(win):
    switches = [a for a in sys.argv[1:] if a.startswith("-")]
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    send_address = args.pop(0) if args and args[0].startswith("/") else "//localhost"
    recv_address = args.pop(0) if args and args[0].startswith("/") else send_address

    win.nodelay(1)
    coll = Collector()
    drv = Driver(coll, Client(win, send_address, recv_address, notify=("-n" in switches)))
    drv.run()

curses.wrapper(main)
