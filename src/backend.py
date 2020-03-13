import sys
import Pyro4
import Pyro4.errors


@Pyro4.behavior(instance_mode='single')
class Backend():
    def __init__(self):
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
        pass

    @Pyro4.expose
    def propogate(self, u_id, resp):
        pass

    @Pyro4.expose
    def getItem(self, store, order_item, u_id):
        if u_id in self._responses:
            item = self._responses[u_id]
        else:
            item = self._db[store][order_item]
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
                    return []
        return item

    @Pyro4.expose
    def getItemName(self, store, order_item, u_id):
        if u_id in self._responses:
            item_name = self._responses[u_id]
        else:
            item_name = self._db[store][order_item][0]
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
                    return ''
        return item_name

    @Pyro4.expose
    def getItems(self, store, u_id):
        if u_id in self._responses:
            items = self._responses[u_id]
        else:
            items = self._db[store]
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
                    return []
        return items

    @Pyro4.expose
    def getStoreName(self, store, u_id):
        pass

    @Pyro4.expose
    def placeOrder(self, store, order_item, quant, address, u_id):
        pass

    @Pyro4.expose
    def finaliseOrder(self, store, order_item, quant, address, client_id, u_id):
        pass

    @Pyro4.expose
    def clientId(self):
        pass
