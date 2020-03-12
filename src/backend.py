import sys
import Pyro4
import Pyro4.errors


class Backend():
    def __init__(self):
        self._backups = []
        self._db = {
            'General Store': [['Potato', 0.24, 300],
                              ['Carrot', 0.05, 5000],
                              ['Pizza', 4, 50],
                              ['Cake', 7, 100],
                              ['Loaf of Bread', 0.5, 10000]],
            'Secret Shop': [['Mango', 0.85, 1000],
                            ['Enchanted Mango', 500, 2],
                            ['Magic Beans', 200, 3],
                            ['Dragon Fruit', 2, 300]]
        }


    def find_backups(self):
        pass
