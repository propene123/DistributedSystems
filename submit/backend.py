import sys
import copy
import Pyro4
import Pyro4.errors
import Pyro4.configuration

# ensure requests are dealt with sequentially (message ordering)
Pyro4.config.SERVERTYPE = 'multiplex'

NAME = ''


@Pyro4.behavior(instance_mode='single')
class Backend():
    def __init__(self):
        # init server data
        self._name = NAME
        self._backups = []
        self._clientID = 1
        self._responses = {}
        self._orders = {}
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
                # search for backup servers
                for backup, backup_uri in ns.list(prefix='justHungry.backend.').items():
                    if backup != f'justHungry.backend.{self._name}':
                        backup_proxy = Pyro4.Proxy(backup_uri)
                        exists = False
                        for entry in self._backups:
                            if backup == entry[0]:
                                exists = True
                        if exists:
                            continue
                        try:
                            # pass current state of primary to backup
                            res = backup_proxy.initBackup(self._db, self._responses, self._orders, self._clientID)
                            if not res:
                                try:
                                    # if backup dead de register it from nameserver
                                    with Pyro4.locateNS() as ns:
                                        ns.remove(name=backup)
                                except Pyro4.errors.NamingError:
                                    pass
                            else:
                                # add to the listof good backups
                                self._backups.append([backup, backup_proxy])
                        except Pyro4.errors.PyroError:
                            try:
                                # remove dead backup from nameserver
                                with Pyro4.locateNS() as ns:
                                    ns.remove(name=backup)
                            except Pyro4.errors.NamingError:
                                pass
        except Pyro4.errors.NamingError:
            pass

    @Pyro4.expose
    def initBackup(self, db, resp, new_orders, new_client_id):
        self._responses = copy.deepcopy(resp)
        self._db = db[::]
        self._orders = copy.deepcopy(new_orders)
        self._clientID = new_client_id
        return True

    @Pyro4.expose
    def propogate(self, u_id, resp, new_db, new_orders, new_client_id):
        self._responses[u_id] = resp
        self._db = new_db[::]
        self._orders = copy.deepcopy(new_orders)
        self._clientID = new_client_id
        return True

    @Pyro4.expose
    def getItem(self, store, order_item, u_id):
        # look for any new backup servers
        self.find_backups()
        if u_id in self._responses:
            item = self._responses[u_id]
        else:
            try:
                item = self._db[store][1][order_item]
            except:
                item = []
            self._responses[u_id] = item
        return item


    @Pyro4.expose
    def getOrders(self, client_id, u_id):
        self.find_backups()
        if u_id in self._responses:
            orders = self._responses[u_id]
        else:
            try:
                orders = self._orders[client_id]
            except:
                orders = []
            self._responses[u_id] = orders
        return orders


    @Pyro4.expose
    def getItemName(self, store, order_item, u_id):
        self.find_backups()
        if u_id in self._responses:
            item_name = self._responses[u_id]
        else:
            try:
                item_name = self._db[store][1][order_item][0]
            except:
                item_name = ''
            self._responses[u_id] = item_name
        return item_name

    @Pyro4.expose
    def getItems(self, store, u_id):
        self.find_backups()
        if u_id in self._responses:
            items = self._responses[u_id]
        else:
            try:
                items = self._db[store][1]
            except:
                items = ['ERROR']
            self._responses[u_id] = items
        return items

    @Pyro4.expose
    def getStoreName(self, store, u_id):
        self.find_backups()
        if u_id in self._responses:
            store_name = self._responses[u_id]
        else:
            try:
                store_name = self._db[store][0]
            except:
                store_name = ''
            self._responses[u_id] = store_name
        return store_name

    @Pyro4.expose
    def getStores(self, u_id):
        self.find_backups()
        if u_id in self._responses:
            stores = self._responses[u_id]
        else:
            stores = []
            for store in self._db:
                stores.append(store[0])
            self._responses[u_id] = stores
        return stores

    @Pyro4.expose
    def placeOrder(self, store, order_item, quant, u_id):
        self.find_backups()
        if u_id in self._responses:
            valid = self._responses[u_id]
        else:
            valid = (0 < quant <= self._db[store][1][order_item][2])
            self._responses[u_id] = valid
        return valid

    @Pyro4.expose
    def finaliseOrder(self, store, order_item, quant, address, client_id, u_id):
        self.find_backups()
        resp = False
        if u_id in self._responses:
            resp = self._responses[u_id]
        else:
            resp = (0 < quant <= self._db[store][1][order_item][2])
            if not resp:
                return False
            # process order
            self._responses[u_id] = resp
            self._db[store][1][order_item][2] -= quant
            if client_id not in self._orders:
                self._orders[client_id] = []
            self._orders[client_id].append(
                [self._db[store][0], self._db[store][1][order_item][0], quant, quant*self._db[store][1][order_item][1], address])
            # go through all backup servers
            for backup in self._backups[::]:
                try:
                    # try to propogate order
                    res = backup[1].propogate(
                        u_id, client_id, self._db, self._orders, self._clientID)
                    if not res:
                        try:
                            # if failed remove that backup
                            with Pyro4.locateNS() as ns:
                                ns.remove(name=backup[0])
                                self._backups.remove(backup)
                        # on comm error undo the order and return error
                        except Pyro4.errors.NamingError:
                            self._db[store][1][order_item][2] += quant
                            self._responses[u_id] = False
                            self._orders[client_id].pop()
                            return False
                # remove dead backups
                except Pyro4.errors.PyroError:
                    try:
                        with Pyro4.locateNS() as ns:
                            ns.remove(name=backup[0])
                            self._backups.remove(backup)
                    # on comm error undo order and return error
                    except Pyro4.errors.NamingError:
                        self._db[store][1][order_item][2] += quant
                        self._responses[u_id] = False
                        self._orders[client_id].pop()
                        return False
        return resp

    @Pyro4.expose
    def clientId(self, u_id):
        self.find_backups()
        client_id = None
        if u_id in self._responses:
            client_id = self._responses[u_id]
        else:
            client_id = self._clientID
            self._clientID += 1
            self._responses[u_id] = client_id
            for backup in self._backups[::]:
                try:
                    res = backup[1].propogate(
                        u_id, client_id, self._db, self._orders, self._clientID)
                    if not res:
                        try:
                            with Pyro4.locateNS() as ns:
                                ns.remove(name=backup[0])
                                self._backups.remove(backup)
                        except Pyro4.errors.NamingError:
                            self._clientID -= 1
                            self._responses[u_id] = None
                            return None
                except Pyro4.errors.PyroError:
                    try:
                        with Pyro4.locateNS() as ns:
                            ns.remove(name=backup[0])
                            self._backups.remove(backup)
                    except Pyro4.errors.NamingError:
                        self._clientID -= 1
                        self._responses[u_id] = None
                        return None
        return client_id

    @Pyro4.expose
    def notifyPrimary(self):
        return True


# parse args
if len(sys.argv) < 2 or len(sys.argv) > 2:
    sys.exit('backend should be called with 1 argument, a unique id for the server')
NAME = sys.argv[1]

# attempt to register with nameserver
try:
    with Pyro4.Daemon() as daemon:
        backend_uri = daemon.register(Backend)
        try:
            with Pyro4.locateNS() as ns:
                ns.register('justHungry.backend.'+NAME, backend_uri)
        except Pyro4.errors.NamingError:
            sys.exit('Could not find nameserver. EXITING')
        daemon.requestLoop()
except Pyro4.errors.DaemonError:
    sys.exit('Pyro daemon has crashed. EXITING')
