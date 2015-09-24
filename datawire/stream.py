# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

import logging, time
try:
    import sqlite3
    def dbapi_connect(name):
        return sqlite3.connect(name)
    dbapi_Binary = sqlite3.Binary
except:
    from com.ziclix.python.sql import zxJDBC
    def dbapi_connect(name):
        return zxJDBC.connect("jdbc:sqlite:"+name, "", "", "org.sqlite.JDBC")
    dbapi_Binary = zxJDBC.Binary
from proton import Message, Endpoint
from proton.reactor import Reactor
from proton.handlers import CFlowController, CHandshaker
from .impl import dual_impl
from .decoder import Decoder
log = logging.getLogger(__name__)

@dual_impl(depends=["Store"])
class Entry:

    def __init__(self, msg, persistent=True, deleted = False):
        self.message = msg
        self.persistent = persistent
        self.deleted = deleted
        self.timestamp = time.time()

@dual_impl
class Store:

    def __init__(self, name=None):
        self.name = name
        if self.name:
            self.db = dbapi_connect(self.name)
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
        self.last_idle = 0
        self.max_idle = 0
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
                                    (serial, dbapi_Binary(entry.message)))
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
                                (self.serial + idx, dbapi_Binary(entry.message)))
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

        now = time.time()
        if self.entries:
            self.max_idle = max(now - self.entries[0].timestamp, self.max_idle)

        if serial == self.lastgc:
            return 0

        if self.serial < serial:
            delta = serial - self.serial
            tail = self.compact(self.entries[:delta])
            reclaimed = delta - len(tail)
            self.last_idle = now - self.entries[reclaimed - 1].timestamp
            self.max_idle = max(self.last_idle, self.max_idle)
            self.entries[:delta] = tail
            self.serial += reclaimed
            if self.db:
                self._update(reclaimed, len(tail))
        else:
            reclaimed = 0

        self.lastgc = serial
        return reclaimed

    def compact(self, tail):
        return []

    def reader(self, address=None):
        reader = Reader(self)
        reader.address = address
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

@dual_impl
class MultiStore:

    def __init__(self):
        self.stores = {}
        self.size = 0
        self.last_idle = 0
        self.max_idle = 0

    def gc(self):
        for k in self.stores.keys()[:]:
            s = self.stores[k]
            self.size -= s.gc()
            self.last_idle = s.last_idle
            self.max_idle = max(self.max_idle, s.max_idle)
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
        self.size += 1

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

@dual_impl
class Stream:

    def __init__(self, store = None):
        self.store = store or Store()
        self.handlers = [CFlowController(), CHandshaker(), Decoder()]
        self.incoming = []
        self.outgoing = []
        self.message = Message()
        self.closed = False

    def put(self, msg):
        if isinstance(msg, Message):
            self.store.put(msg.encode(), address=msg.address)
        else:
            self.message.body = msg
            self.store.put(self.message.encode())

    def close(self):
        self.closed = True

    def on_link_local_open(self, event):
        self.setup(event)

    def on_link_remote_open(self, event):
        self.setup(event)

    def setup(self, event):
        snd = event.sender
        if snd and not hasattr(snd, "reader"):
            rsa = snd.remote_source.address
            lsa = snd.source.address
            rta = snd.remote_target.address
            lta = snd.target.address
            snd.reader = self.store.reader(rsa or lsa or
                                           rta or lta)
            self.outgoing.append(snd)
        elif event.receiver and event.receiver not in self.incoming:
            rcv = event.receiver
            self.incoming.append(rcv)

    def on_link_final(self, event):
        if event.sender:
            event.sender.reader.close()
            self.outgoing.remove(event.sender)
        else:
            self.incoming.remove(event.receiver)

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
        self.queued = 0
        for snd in self.outgoing:
            self.pump_sender(snd)
            self.queued += snd.queued
        self.store.gc()
        self.store.flush()

    def on_reactor_quiesced(self, event):
        self.pump()

    ctr = 0
    def on_encoded_message(self, event):
        rcv = event.receiver
        dlv = event.delivery
        if rcv and not dlv.partial:
            try:
                self.ctr += 1
                msg = dlv.encoded
            except:
                raise
            address = rcv.target.address
            self.store.put(msg, address=address)
            log.debug("incoming delivery=%s", dlv);
            dlv.settle()

    def _matches(self, host, port, address, link):
        if host is None:
            return False
        else:
            if link.is_sender:
                terminus = link.target
            else:
                terminus = link.source
            return (link.connection.hostname == "%s:%s" % (host, port) and
                    terminus.address == address)

    def relink(self, sender=True, receiver=True, host=None, port=None, address=None):
        log.debug("relinking stream: sender=%s, receiver=%s", sender, receiver)
        if sender:
            for l in self.outgoing:
                if self._matches(host, port, address, l):
                    log.debug("omitting spurious relink")
                else:
                    l._relink = True
                    l.close()
        if receiver:
            for l in self.incoming:
                if self._matches(host, port, address, l):
                    log.debug("omitting spurious relink")
                else:
                    l._relink = True
                    l.close()
