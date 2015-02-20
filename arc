#!/usr/bin/env python

import argparse, curses, textwrap, time, sys, os
from datetime import datetime
from curses import ascii
from proton import Message
from proton.reactor import Reactor
from datawire import Stream, Sender, Receiver, Processor

try:
    import dbus
    bus = dbus.SessionBus()
    notifications = dbus.Interface(bus.get_object("org.freedesktop.Notifications",
                                                  "/org/freedesktop/Notifications"),
                                                  "org.freedesktop.Notifications")
except ImportError:
    notifications = None
except dbus.exceptions.DBusException:
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

class Client:

    def __init__(self, win, send_address, recv_address, notify=False, echo=False):
        self.offset = 0
        self.log = []
        self.input = ""
        self.win = win
        self.sel = None
        self.stream = Stream()
        self.sender = Sender(send_address, self.stream)
        self.receiver = Receiver(recv_address, Processor(self))
        self.notify = notify
        self.echo = echo
        self.send_name = send_address
        self.recv_name = recv_address

        self.prev_maxyx = None
        self.handlers = [self.sender, self.receiver]

    def on_reactor_quiesced(self, event):
        maxyx = self.win.getmaxyx()
        if maxyx != self.prev_maxyx:
            self.render()
            self.pref_maxyx = maxyx

    def on_reactor_init(self, event):
        self.sel = event.reactor.selectable()
        self.sel.fileno(0)
        self.sel.reading = True
        event.reactor.update(self.sel)
        self.receiver.start(event.reactor)
        self.sender.start(event.reactor)
        self.render()

    def pp(self, msg):
        if not msg.properties:
            return str(msg.body)
        else:
            return str(msg)

    def abbreviate(self, address):
        return address

    def wrap(self, prefix, text, width):
        if prefix:
            # The textwrap.wrap implementation has an infinite loop in it
            # when you pass it a width less than the length of the prefix.
            # For that reason we establish a minimum width that is 16
            # characters greater than the prefix, also it looks kind of
            # stupid to wrap down to a column of less than 16 characters
            minwidth = len(prefix) + 16
            width = max(minwidth, width)
        return textwrap.wrap(text, width,
                             initial_indent=prefix,
                             subsequent_indent=" "*len(prefix),
                             drop_whitespace=False,
                             replace_whitespace=False)

    def pretty_time(self, t):
        return datetime.fromtimestamp(t).strftime("%a %I:%M%p")

    def on_message(self, event):
        rcv = event.receiver
        msg = event.message
        name = self.abbreviate(msg.user_id or msg.reply_to or rcv.source.address or "")

        notificate = self.notify and name != os.environ["USER"]
        if msg.creation_time:
            if time.time() - msg.creation_time > 60:
                notificate = False
            prefix = "%s <- %s " % (self.pretty_time(msg.creation_time), name)
        else:
            notificate = False
            prefix = "<- %s " % name

        pretty = self.pp(msg)
        self.log.append((prefix, pretty))

        self.render()
        if notificate:
            notify(name, pretty)

    def on_selectable_readable(self, event):
        while True:
            c = self.win.getch()
            if c < 0:
                break
            elif c == 10:
                msg = Message()
                msg.user_id = os.environ["USER"]
                msg.creation_time = time.time()
                if self.input and self.input[0] == "/":
                    parts = self.input.split(None, 1)
                    opcode = parts.pop(0)[1:]
                    msg.properties = {"opcode": unicode(opcode)}
                    if parts:
                        try:
                            msg.body = eval(parts[0])
                        except:
                            self.log.append(("ERROR: ", str(sys.exc_info()[1])))
                            continue
                    else:
                        msg.body = None
                else:
                    msg.body = unicode(self.input)
                self.stream.put(msg)
                if self.echo:
                    prefix = "%s %s -> " % (self.pretty_time(msg.creation_time), self.recv_name)
                    self.log.append((prefix, self.input))
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
                self.sel.terminate()
                event.reactor.update(self.sel)
                self.sendq.close()
                self.recvq.close()
            elif c == curses.KEY_RESIZE:
                pass
            elif ascii.isprint(c):
                self.input = "%s%c" % (self.input, c)
            else:
                self.input = "%s<%s>" % (self.input, c)
        self.render()

    def render(self):
        self.win.clear()
        height, width = self.win.getmaxyx()

        lines = []

        idx = len(self.log)
        offset = self.offset
        while idx > 0:
            idx -= 1
            prefix, text = self.log[idx]
            wrapped = self.wrap(prefix, text, width)
            if not wrapped:
                wrapped = [prefix]
            while wrapped and offset > 0:
                wrapped.pop()
                offset -= 1

            wrapped.reverse()
            lines.extend(wrapped)
            if len(lines) >= height - 2:
                break

        lines.reverse()

        lines.append("="*width)

        input = self.wrap("", self.input, width)
        lines.extend(input)

        if len(lines[-1]) >= width:
            lines.append("")

        if len(lines) > height:
            lines = lines[len(lines) - height:]
        elif len(lines) < height:
            lines = [""]*(height - len(lines)) + lines
        y = 0
        for l in lines:
            self.win.addstr(y, 0, l[:width])
            y += 1
        self.win.refresh()

parser = argparse.ArgumentParser(description="interactive AMQP client")
parser.add_argument("-n", "--notify", action="store_true", help="enable notifications")
parser.add_argument("-e", "--echo", action="store_true", help="enable echo")
parser.add_argument("send_address", default="//localhost", nargs='?', help="send address")
parser.add_argument("recv_address", nargs='?', help="recv address")

args = parser.parse_args()

def main(win):
    win.nodelay(1)
    Reactor(Client(win, args.send_address, args.recv_address or args.send_address, args.notify, args.echo)).run()

curses.wrapper(main)
