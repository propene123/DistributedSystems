# saved as greeting-client.py
import Pyro4

name = input("What is your name? ").strip()

hmm = Pyro4.Proxy("PYRONAME:example.greeting")    # use name server object lookup uri shortcut
with Pyro4.locateNS() as ns:
    print(ns.list())
    ns.remove(prefix='example.greeting')
    print(ns.list())
