# python -m Pyro4.naming

import Pyro4

@Pyro4.expose
class GreetingMaker(object):
    def get_fortune(self):
        print('lol')


daemon = Pyro4.Daemon()                # make a Pyro daemon
ns = Pyro4.locateNS()                  # find the name server
uri = daemon.register(GreetingMaker)   # register the greeting maker as a Pyro object
ns.register("example.greeting", uri)   # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()                   # start the event loop of the server to wait for calls
