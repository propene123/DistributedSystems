import urllib.request
import urllib.error
import json
import sys
import Pyro4
import Pyro4.errors
import Pyro4.configuration


# ensure requests are dealt with sequentially (message ordering)
Pyro4.config.SERVERTYPE = 'multiplex'


@Pyro4.behavior(instance_mode='single')
class Frontend():
    def __init__(self):
        self._u_id = 0
        self._primary = None

    def find_primary(self):
        backends = []
        try:
            with Pyro4.locateNS() as ns:
                for backend, backend_uri in ns.list(prefix='justHungry.backend.').items():
                    backends.append([backend, Pyro4.Proxy(backend_uri)])
        except Pyro4.errors.NamingError:
            return False
        if not backends:
            self._primary = None
            return False
        for backend in backends:
            try:
                success = backend[1].notifyPrimary()
                if success:
                    self._primary = backend
                    return True
                try:
                    with Pyro4.locateNS() as ns:
                        ns.remove(name=backend[0])
                except Pyro4.errors.NamingError:
                    return False
            except Pyro4.errors.PyroError:
                self.remove_primary()
                return self.find_primary()
        self._primary = None

    def remove_primary(self):
        if self._primary is None:
            return
        try:
            with Pyro4.locateNS() as ns:
                ns.remove(name=self._primary[0])
        except Pyro4.errors.NamingError:
            pass
        self._primary = None

    @Pyro4.expose
    def getStores(self):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return ['ERROR']
        try:
            self._u_id += 1
            return self._primary[1].getStores(self._u_id-1)
        except Pyro4.errors.PyroError:
            if not self.find_primary():
                return ['ERROR']
            return self.getStores()

    @Pyro4.expose
    def getItems(self, store):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return ['ERROR']
        try:
            self._u_id += 1
            return self._primary[1].getItems(store, self._u_id-1)
        except Pyro4.errors.PyroError:
            if not self.find_primary():
                return ['ERROR']
            return self.getItems(store)

    @Pyro4.expose
    def getItem(self, store, order_item):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return []
        try:
            self._u_id += 1
            return self._primary[1].getItem(store, order_item, self._u_id-1)
        except Pyro4.errors.PyroError:
            if not self.find_primary():
                return []
            return self.getItem(store, order_item)

    @Pyro4.expose
    def placeOrder(self, store, order_item, quant):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return False
        try:
            self._u_id += 1
            return self._primary[1].placeOrder(store, order_item, quant, self._u_id-1)
        except Pyro4.errors.PyroError:
            if not self.find_primary():
                return False
            return self.placeOrder(store, order_item, quant)

    @Pyro4.expose
    def finaliseOrder(self, store, order_item, quant, address):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return False
        try:
            self._u_id += 1
            return self._primary[1].finaliseOrder(store, order_item, quant, address, self._u_id-1)
        except Pyro4.errors.PyroError:
            if not self.find_primary():
                return False
            return self.finaliseOrder(store, order_item, quant, address, u_id)

    @Pyro4.expose
    def getStoreName(self, store):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return ''
        try:
            self._u_id += 1
            return self._primary[1].getStoreName(store, self._u_id-1)
        except Pyro4.errors.PyroError:
            if not self.find_primary():
                return ''
            return self.getStoreName(store)

    @Pyro4.expose
    def getItemName(self, store, order_item):
        if self._primary is None:
            success = self.find_primary()
            if not success:
                return ''
        try:
            self._u_id += 1
            return self._primary[1].getItemName(store, order_item, self._u_id-1)
        except Pyro4.errors.PyroError:
            if not self.find_primary():
                return ''
            return self.getItemName(store, order_item)

    @Pyro4.expose
    def getAddress(self, postcode):
        result = ''
        try:
            try:
                resp = urllib.request.urlopen('https://api.postcodes.io/' +
                                              'postcodes/' + postcode)
                try:
                    data = json.load(resp)
                    if data['result']['admin_district']:
                        result += (data['result']['admin_district'] + '\n')
                    if data['result']['admin_ward']:
                        result += (data['result']['admin_ward'] + '\n')
                    result += postcode
                except json.JSONDecodeError:
                    return postcode
                return result
            except urllib.error.HTTPError:
                return ''
        except urllib.error.URLError:
            return postcode


try:
    with Pyro4.Daemon() as daemon:
        frontend_uri = daemon.register(Frontend)
        try:
            with Pyro4.locateNS() as ns:
                ns.register('justHungry.frontend', frontend_uri)
        except Pyro4.errors.NamingError:
            sys.exit('Could not find nameserver. EXITING')
        daemon.requestLoop()
except Pyro4.errors.DaemonError:
    sys.exit('Pyro daemon has crashed. EXITING')
