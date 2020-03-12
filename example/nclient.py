# saved as greeting-client.py
import Pyro4

name = input("What is your name? ").strip()

Pyro4.Proxy("PYRONAME:example.greeting")    # use name server object lookup uri shortcut
