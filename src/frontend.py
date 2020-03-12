import Pyro4
import Pyro4.errors


PRIMARY = None


class frontend(object):
    def __init__(self):
        self._primary = None

    def find_primary(self):
        backends = []
        with Pyro4.locateNS() as ns:
            for backend, backend_uri in ns.list(prefix='justHungry.backend.').items():
                backends.append([backend, Pyro4.Proxy(backend_uri)])
        if not backends:
            self._primary = None
            return False
        for backend in backends:
            success = backend[1].notifyPrimary()
            if success:
                self._primary = backend
                return True
            ns.remove(name=backend[0])
        self._primary = None
        return False

    def remove_primary(self):
        if self._primary is None:
            return
        with Pyro4.locateNS() as ns:
            ns.remove(name=self._primary[0])
            self._primary = None

    def check_primary(self):
        try:
            exists = self._primary[1].pingBackend()
            return exists
        except Pyro4.errors.PyroError:
            return False

    @Pyro4.expose
    def getStores(self):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return []
        success = self.check_primary()
        if not success:
            self.remove_primary()
            return []
        return self._primary.getStores()

    @Pyro4.expose
    def getItems(self, store):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return []
        success = self.check_primary()
        if not success:
            self.remove_primary()
            return []
        return self._primary.getItems(store)

    @Pyro4.expose
    def getItem(self, store, order_item):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return []
        success = self.check_primary()
        if not success:
            self.remove_primary()
            return []
        return self._primary.getItems(store, order_item)

    @Pyro4.expose
    def placeOrder(self, store, order_item, quant):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return False
        success = self.check_primary()
        if not success:
            self.remove_primary()
            return False
        return self._primary.placeOrder(store, order_item, quant)

    @Pyro4.expose
    def finaliseOrder(self, store, order_item, quant, address):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return False
        success = self.check_primary()
        if not success:
            self.remove_primary()
            return False
        return self._primary.finaliseOrder(store, order_item, quant, address)

    @Pyro4.expose
    def getStoreName(self, store):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return ''
        success = self.check_primary()
        if not success:
            self.remove_primary()
            return ''
        return self._primary.getStoreName(store)

    @Pyro4.expose
    def getItemName(self, store, order_item):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return ''
        success = self.check_primary()
        if not success:
            self.remove_primary()
            return ''
        return self._primary.getItemName(store, order_item)


