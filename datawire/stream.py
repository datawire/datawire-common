# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited. 

import sqlite3, logging
from proton import Message, Endpoint
from proton.reactor import Reactor
from proton.handlers import CFlowController, CHandshaker

log = logging.getLogger(__name__)

class Entry:

    def __init__(self, msg, persistent=True, deleted = False):
        self.message = msg
        self.persistent = persistent
        self.deleted = deleted

class Store:

    def __init__(self, name=None):
        self.name = name
        if self.name:
            self.db = sqlite3.connect(self.name)
            if not list(self.db.execute('pragma table_info(streams)')):
                log.info("%s: creating schema", self.name)
                self.db.execute('''create table streams (serial integer,
                                                         message blob,
                                                         primary key(serial))''')
        else:
            self.db = None
        self.serial = 0
        self.entries = []
        self.readers = []
        self.lastgc = 0
        if self.db:
            self._recover()

    def _recover(self):
        serial = None
        for row in self.db.execute('select serial, message from streams order by serial'):
            if serial is None:
                serial = row[0]
                self.serial = serial
            else:
                while serial < row[0] - 1:
                    self.entries.append(Entry(None, persistent=False, deleted=True))
                    serial += 1
                assert row[0] == serial + 1
                serial = row[0]
            log.debug("%s: recovering %s", self.name, serial)
            self.put(str(row[1]))
        self.lastgc = self.min()
        self.lastflush = self.max()

    def start(self):
        return self.min()

    def put(self, msg, persistent=True, address=None):
        self.entries.append(Entry(msg, persistent=persistent))

    def max(self):
        return self.serial + len(self.entries)

    def min(self):
        return self.serial

    def get(self, serial):
        return self.entries[serial - self.serial]

    def flush(self):
        if self.db:
            for serial in range(self.lastflush, self.max()):
                entry = self.entries[serial - self.serial]
                if entry.persistent:
                    log.debug("%s: insert %s, %r", self.name, serial, entry.message)
                    self.db.execute("insert into streams (serial, message) values (?, ?)",
                                    (serial, sqlite3.Binary(entry.message)))
            self.db.commit()
        self.lastflush = self.max()

    def _update(self, deleted, updated):
        commit = False
        if self.serial - deleted < self.lastflush:
            log.debug("%s: delete < %s", self.name, self.serial)
            self.db.execute("delete from streams where serial < ?", (self.serial,))
            commit = True
        for idx in range(0, updated):
            entry = self.entries[idx]
            if entry.persistent:
                log.debug("%s: update %s, %r", self.name, self.serial + idx, entry.message)
                self.db.execute("insert or replace into streams (serial, message) values (?, ?)",
                                (self.serial + idx, sqlite3.Binary(entry.message)))
            else:
                log.debug("%s: delete %s", self.name, self.serial + idx)
                self.db.execute("delete from streams where serial = ?", (self.serial + idx,))
            commit = True
        if commit:
            self.db.commit()
        if self.lastflush < self.serial + updated:
            self.lastflush = self.serial + updated

    def gc(self):
        serial = self.max()
        for r in self.readers:
            serial = min(r.serial, serial)

        if serial == self.lastgc:
            return

        if self.serial < serial:
            delta = serial - self.serial
            tail = self.compact(self.entries[:delta])
            self.entries[:delta] = tail
            self.serial += delta - len(tail)
            if self.db:
                self._update(delta - len(tail), len(tail))

        self.lastgc = serial

    def compact(self, tail):
        return []

    def reader(self, address=None):
        reader = Reader(self)
        self.readers.append(reader)
        return reader

class Reader:

    def __init__(self, store):
        self.store = store
        self.serial = store.min()

    def next(self):
        if self.more():
            while True:
                result = self.store.get(self.serial)
                self.serial += 1
                if not result.deleted:
                    break
            return result
        else:
            return None

    def more(self):
        return self.serial < self.store.max()

    def close(self):
        self.store.readers.remove(self)


class MultiStore:

    def __init__(self):
        self.stores = {}

    def gc(self):
        for k in self.stores.keys()[:]:
            s = self.stores[k]
            s.gc()
            if not s.readers and not s.entries:
                log.debug("removing store for %s", k)
                del self.stores[k]

    def flush(self):
        for s in self.stores.values():
            s.flush()

    def put(self, msg, address=None):
        if address in self.stores:
            store = self.stores[address]
        else:
            log.debug("resolving (put) %s", address)
            store = self.resolve(address)
            if store is None:
                return
            self.stores[address] = store
        store.put(msg)

    def resolve(self, address):
        return Store()

    def reader(self, address):
        if address in self.stores:
            store = self.stores[address]
        else:
            log.debug("resolving (get) %s", address)
            store = self.resolve(address)
            if store is None:
                return None
            self.stores[address] = store
        return store.reader(address)

class Stream:

    def __init__(self, store = None):
        self.store = store or Store()
        self.handlers = [CFlowController(), CHandshaker()]
        self.outgoing = []
        self.message = Message()
        self.closed = False

    def put(self, msg):
        if isinstance(msg, Message):
            self.store.put(msg.encode(), address=msg.address)
        else:
            self.message.body = msg
            self.store.put(self.message.encode(), address=msg.address)

    def close(self):
        self.closed = True

    def on_link_local_open(self, event):
        self.setup(event)

    def on_link_remote_open(self, event):
        self.setup(event)

    def setup(self, event):
        snd = event.sender
        if snd and not hasattr(snd, "reader"):
            snd.reader = self.store.reader(snd.remote_source.address or snd.source.address or
                                           snd.remote_target.address or snd.target.address)
            self.outgoing.append(snd)

    def on_link_final(self, event):
        if event.sender:
            event.sender.reader.close()
            self.outgoing.remove(event.sender)

    def on_link_flow(self, event):
        if event.sender:
            self.pump_sender(event.sender)

    def pump_sender(self, snd):
        while snd.reader.more() and snd.credit > 0 and snd.queued < 1024:
            entry = snd.reader.next()
            dlv = snd.delivery(snd.delivery_tag())
            snd.send(entry.message)
            dlv.settle()
        if not snd.reader.more():
            snd.drained()
            if self.closed:
                snd.close()

    def pump(self):
        for snd in self.outgoing:
            self.pump_sender(snd)
        self.store.gc()
        self.store.flush()

    def on_reactor_quiesced(self, event):
        self.pump()

    def on_delivery(self, event):
        rcv = event.receiver
        dlv = event.delivery
        if rcv and not dlv.partial:
            msg = rcv.recv(dlv.pending)
            address = rcv.target.address
            self.store.put(msg, address=address)
            dlv.settle()
