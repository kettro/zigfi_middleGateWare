# Imports
#from db import Database
#from znetwork import ZNetwork

class CommandInterpreter:
    def __init__(self):
        # Instantiate the ZNetwork
        #self.znet = ZNetwork()
        # Instantiate the Database
        self.db = Database('db.json')
        return

    # Has functions to interpret incoming commands
    # Needs a sort of translation table?

    def interpret(message):
        # Assume that the message is at this point parsed, but nothing more
        valid = true # valid is assumed true
        return


