import sys
import Pyro4
import Pyro4.errors
import Pyro4.configuration

# ensure requests are dealt with sequentially (message ordering)
Pyro4.config.SERVERTYPE = 'multiplex'

NAME = ''


@Pyro4.behavior(instance_mode='single')
class Backend():
    def __init__(self):
        self._name = NAME
        self._backups = []
        self._clientID = 0
        self._responses = {}
        self._db = [
            ['General Store', [['Potato', 0.24, 300],
                               ['Carrot', 0.05, 5000],
                               ['Pizza', 4, 50],
                               ['Cake', 7, 100],
                               ['Loaf of Bread', 0.5, 10000]]],
            ['Secret Shop', [['Mango', 0.85, 1000],
                             ['Enchanted Mango', 500, 2],
                             ['Magic Beans', 200, 3],
                             ['Dragon Fruit', 2, 300]]]
        ]

    def find_backups(self):
        try:
            with Pyro4.locateNS() as ns:
                for backup, backup_uri in ns.list(prefix='justHungry.backend.'):
                    if backup != self._name:
                        self._backups.append([backup, Pyro4.Proxy(backup_uri)])
        except Pyro4.errors.NamingError:
            pass

    @Pyro4.expose
    def propogate(self, u_id, resp, new_db):
        self._responses[u_id] = resp
        self._db = new_db[::]
        return True

    @Pyro4.expose
    def getItem(self, store, order_item, u_id):
        if u_id in self._responses:
            item = self._responses[u_id]
        else:
            item = self._db[store][1][order_item]
            self._responses[u_id] = item
            for backup in self._backups[:]:
                try:
                    res = backup[1].propogate(u_id, item)
                    if not res:
                        try:
                            with Pyro4.locateNS() as ns:
                                ns.remove(name=backup[0])
                                self._backups.remove(backup)
                        except Pyro4.errors.NamingError:
                            return []
                except Pyro4.errors.PyroError:
                    try:
                        with Pyro4.locateNS() as ns:
                            ns.remove(name=backup[0])
                            self._backups.remove(backup)
                    except Pyro4.errors.NamingError:
                        return []
        return item

    @Pyro4.expose
    def getItemName(self, store, order_item, u_id):
        if u_id in self._responses:
            item_name = self._responses[u_id]
        else:
            item_name = self._db[store][1][order_item][0]
            self._responses[u_id] = item_name
            for backup in self._backups[:]:
                try:
                    res = backup[1].propogate(u_id, item_name)
                    if not res:
                        try:
                            with Pyro4.locateNS() as ns:
                                ns.remove(name=backup[0])
                                self._backups.remove(backup)
                        except Pyro4.errors.NamingError:
                            return ''
                except Pyro4.errors.PyroError:
                    try:
                        with Pyro4.locateNS() as ns:
                            ns.remove(name=backup[0])
                            self._backups.remove(backup)
                    except Pyro4.errors.NamingError:
                        return ''
        return item_name

    @Pyro4.expose
    def getItems(self, store, u_id):
        if u_id in self._responses:
            items = self._responses[u_id]
        else:
            items = self._db[store][1]
            self._responses[u_id] = items
            for backup in self._backups[:]:
                try:
                    res = backup[1].propogate(u_id, items)
                    if not res:
                        try:
                            with Pyro4.locateNS() as ns:
                                ns.remove(name=backup[0])
                                self._backups.remove(backup)
                        except Pyro4.errors.NamingError:
                            return []
                except Pyro4.errors.PyroError:
                    try:
                        with Pyro4.locateNS() as ns:
                            ns.remove(name=backup[0])
                            self._backups.remove(backup)
                    except Pyro4.errors.NamingError:
                        return []
        return items

    @Pyro4.expose
    def getStoreName(self, store, u_id):
        if u_id in self._responses:
            store_name = self._responses[u_id]
        else:
            store_name = self._db[store][0]
            self._responses[u_id] = store_name
            for backup in self._backups[:]:
                try:
                    res = backup[1].propogate(u_id, store_name)
                    if not res:
                        try:
                            with Pyro4.locateNS() as ns:
                                ns.remove(name=backup[0])
                                self._backups.remove(backup)
                        except Pyro4.errors.NamingError:
                            return ''
                except Pyro4.errors.PyroError:
                    try:
                        with Pyro4.locateNS() as ns:
                            ns.remove(name=backup[0])
                            self._backups.remove(backup)
                    except Pyro4.errors.NamingError:
                        return ''
        return store_name

    @Pyro4.expose
    def placeOrder(self, store, order_item, quant, address, u_id):
        if u_id in self._responses:
            valid = self._responses[u_id]
        else:
            valid = (0 < quant <= self._db[store][1][order_item][2])
            self._responses[u_id] = valid
            for backup in self._backups[:]:
                try:
                    res = backup[1].propogate(u_id, valid)
                    if not res:
                        try:
                            with Pyro4.locateNS() as ns:
                                ns.remove(name=backup[0])
                                self._backups.remove(backup)
                        except Pyro4.errors.NamingError:
                            return False
                except Pyro4.errors.PyroError:
                    try:
                        with Pyro4.locateNS() as ns:
                            ns.remove(name=backup[0])
                            self._backups.remove(backup)
                    except Pyro4.errors.NamingError:
                        return False
        return valid

    @Pyro4.expose
    def finaliseOrder(self, store, order_item, quant, address, client_id, u_id):
        if u_id in self._responses:
            resp = self._responses[u_id]
        else:
            resp = (0 < quant <= self._db[store][1][order_item][2])
            self._responses[u_id] = resp
            self._db[store][1][order_item][2] - quant
            for backup in self._backups[:]:
                try:
                    res = backup[1].propogate(u_id, resp, self._db)
                    if not res:
                        try:
                            with Pyro4.locateNS() as ns:
                                ns.remove(name=backup[0])
                                self._backups.remove(backup)
                        except Pyro4.errors.NamingError:
                            return False
                except Pyro4.errors.PyroError:
                    try:
                        with Pyro4.locateNS() as ns:
                            ns.remove(name=backup[0])
                            self._backups.remove(backup)
                    except Pyro4.errors.NamingError:
                        return False
        return resp

    @Pyro4.expose
    def clientId(self):
        pass

    @Pyro4.expose
    def notifyPrimary(self):
        return True


if len(sys.argv) < 2 or len(sys.argv) > 2:
    sys.exit('backend should be called with 1 argument, a unique id for the server')
NAME = sys.argv[1]

try:
    with Pyro4.Daemon() as daemon:
        backend_uri = daemon.register(Backend)
        try:
            with Pyro4.locateNS() as ns:
                ns.register('justHungry.frontend', backend_uri)
        except Pyro4.errors.NamingError:
            sys.exit('Could not find nameserver. EXITING')
        daemon.requestLoop()
except Pyro4.errors.DaemonError:
    sys.exit('Pyro daemon has crashed. EXITING')
