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
        valid = True # valid is assumed true
        cmd = message['cmd']
        payload = message['payload']
        # "switch" on the cmd
        response = self.cmd_switch(cmd, payload)

        return response

    def cmd_switch(self,cmd, payload):
        '''
        Doing some partial functions; splitting up the workload
        '''
        cmd_bits = cmd.split('_')
        switch = {
                'create': self.create,
                'read': self.read,
                'update': self.update,
                'destroy': self.destroy
                }
        print switch[cmd_bits[0]]
        response = switch[cmd_bits[0]](cmd_bits[1], payload)
        return { 'cmd': cmd, 'response': response }

    def create(self, cmd, payload):
        # Purely metadata: not actually doing anything to the network
        # When implemented; creating a device may change the grouping
        response = payload
        if(cmd == 'grp'):
            # TODO: Search the db for the grp_name: invalid if not empty
            grp_name = payload['grp_name']
            if self.db.create_grp(grp_name) is not -1:
                valid = 0
            else: valid = 4 # Create Error
        elif(cmd == 'dev'):
            if self.db.create_dev(payload) is not -1:
                valid = 0
            else: valid = 4 # Create Error
        response['valid'] = valid
        return response

    def read(self, cmd, payload):
        response = { 'manifest': [] }
        if(cmd == 'connman'):
            # Read Manifest of all connected devices
            # Query the network for currently connected items

            response['manifest'] = self.db.read_connman()
        elif(cmd == 'unconnman'):
            return
        elif(cmd == 'grpman'):
            grp_manifest = self.db.read_grpman()
            entry = {}
            print grp_manifest
            for grp in grp_manifest:
                entry = {}
                print grp
                entry['grp_name'] = grp['grp_name']
                response['manifest'].append(entry)
        elif(cmd == 'devman'):
            grp = payload['grp_name']
            dev_manifest = self.db.read_devman(grp)
            response['grp_name'] = grp
            for dev in dev_manifest:
                entry = {}
                entry['name'] = dev['name']
                entry['type'] = dev['type']
                entry['id'] = dev['id']
                response['manifest'].append(entry)
        elif(cmd == 'ctrlman'):
            return
        elif(cmd == 'devdata'):
            return
        return response

    def update(self, cmd, payload):
        response = payload
        if(cmd == 'grp'):
            return
        if(cmd == 'dev'):
            return
        if(cmd == 'devdata'):
            return
        return response

    def destroy(self, cmd, payload):
        response = payload
        if(cmd == 'grp'):
            return
        elif(cmd == 'dev'):
            return
        return response

