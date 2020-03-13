README:
A minimum python version of 3.6.9 is required to run the python files.
The files can be run on Linux or Windows (performance is better on Linux).
Before running the files you must install Pyro4 using this command:
python -m pip install Pyro4
or on Linux
python3 -m pip install Pyro4

Running the system:
1. Start the nameserver using the command:
   python -m Pyro4.naming
   or on Linux
   python3 -m Pyro4.naming
2. Start the front end using the command:
   python frontend.py
   or on Linux
   python3 frontend.py
3. Start 3 backends using the command:
   python backend.py <ENTER A UNIQUE NAME HERE>
   or on Linux
   python3 backend.py <ENTER A UNIQUE NAME HERE>
4. Start the client using the command:
   python client.py
   or on Linux
   python3 client.py
5. Interact with the system using the client

More Information:
To test the fault tolerance of the system close different combinations of the backend
and frontend programs during operation.
The only external service I have used is the postcode.io api to validate addresses.

