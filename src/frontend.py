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
