from proton.handlers import CHandshaker

def ancestors(address):
    yield address
    if address is None: return
    address = address.split("?", 1)[0]
    path = address.split("/")[:-1]
    while path:
        addr = "/".join(path)
        yield "%s/" % addr
        yield addr
        path.pop()

class Container:

    def __init__(self):
        self.tree = {}
        self.handlers = [CHandshaker()]

    def __setitem__(self, address, handler):
        self.tree[address] = handler

    def __getitem__(self, address):
        for prefix in ancestors(address):
            if prefix in self.tree:
                return self.tree[prefix]
        return None

    def on_link_remote_open(self, event):
        link = event.link
        if link.is_sender:
            address = link.remote_source.address
        else:
            address = link.remote_target.address
        link.handler = self[address]
        if link.handler:
            event.dispatch(link.handler)

    def on_reactor_quiesced(self, event):
        for h in self.tree.values():
            event.dispatch(h)

    def on_transport_closed(self, event):
        event.connection.free()
