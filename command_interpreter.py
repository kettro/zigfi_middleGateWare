# Imports
from db import Database

class CommandInterpreter:
    def __init__(self):
        # Instantiate the Database
        self.db = Database('db.json')
        return

    # Honestly, I think that maybe the db should be in charge of interfacing with
    # the ZNetwork. It is going to end up being the one that actually does the thing anyways...
    # Has functions to interpret incoming commands
    # Needs a sort of translation table?

    def interpret(self, message):
        # Assume that the message is at this point parsed, but nothing more
        valid = true # valid is assumed true
        cmd = message['cmd']
        payload = message['payload']
        # "switch" on the cmd
        response = cmd_switch(cmd, payload)

        return response

    def cmd_switch(cmd, payload):
        '''
        Doing some partial functions; splitting up the workload
        '''
        cmd_bits = cmd.split('_')
        switch = {
                'create': create,
                'read': read,
                'update': update,
                'destroy': destroy
                }
        response = switch[cmd_bits[0]](cmd_bits(1), payload)
        return { 'cmd': cmd, 'response': response }

    def create(cmd, payload):
        # Purely metadata: not actually doing anything to the network
        # When implemented; creating a device may change the grouping
        response = payload
        if(cmd == 'grp'):
            grp_name = payload['grp_name']
            if create_grp(grp_name) is not -1:
                valid = 0
            else: valid = 4 # Create Error
        elif(cmd == 'dev'):
            if create_dev(payload) is not -1:
                valid = 0
            else: valid = 4 # Create Error
            response['']
            break
        response['valid'] = valid
        return response

    def read(cmd, payload):
        response = { 'manifest': [] }
        if(cmd == 'connman'):
            # Read Manifest of all connected devices
            # Query the network for currently connected items
            # 
            break
        elif(cmd == 'unconnman'):
            break
        elif(cmd == 'grpman'):
            break
        elif(cmd == 'devman'):
            break
        elif(cmd == 'ctrlman'):
            break
        elif(cmd == 'devdata'):
            break
        return response

    def update(cmd, payload):
        response = payload
        if(cmd == 'grp'):
            return
        if(cmd == 'dev'):
            return
        if(cmd == 'devdata'):
            break
        return response

    def destroy(cmd, payload):
        response = payload
        if(cmd == 'grp'):
            break
        elif(cmd == 'dev'):
            break
        return response

