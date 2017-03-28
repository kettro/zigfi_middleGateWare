from db import Database


class CommandInterpreter:
    '''
    '''
    def __init__(self):
        '''
        Initialize the database
        '''
        # Instantiate the Database
        self.db = Database('db.json')
        return

    def interpret(self, message):
        '''
        Public access to interpreter utility
        Process the message, and produce a response
        Params:
            message: Parsed message dict, with cmd and payload fields
        Return a dict with fields specific to the cmd
        '''
        # Assume that the message is at this point parsed, but nothing more
        cmd = message['cmd']
        payload = message['payload']
        # "switch" on the cmd
        response = self.__cmd_switch(cmd, payload)

        return response

    def __cmd_switch(self, cmd, payload):
        '''
        Doing some partial functions; splitting up the workload
        '''
        cmd_bits = cmd.split('_')
        switch = {
            'create': self.__create,
            'read': self.__read,
            'update': self.__update,
            'destroy': self.__destroy
        }
        print switch[cmd_bits[0]]
        response = switch[cmd_bits[0]](cmd_bits[1], payload)
        return {'cmd': cmd, 'response': response}

    def __create(self, cmd, payload):
        '''
        Execute the Create commands, based on the cmd; Private access
        Params:
            cmd: Command to be executed, part of the original cmd passed
            payload: arguments passed along with the cmd, specific to the cmd.
        Returns: Response dict to be added as the response in the reply packet
        '''
        # Purely metadata: not actually doing anything to the network
        # When implemented; creating a device may change the grouping
        response = payload
        if(cmd == 'grp'):
            # TODO: Search the db for the grp_name: invalid if not empty
            grp_name = payload['grp_name']
            if self.db.create_grp(grp_name) is not -1:
                valid = 0
            else:
                valid = 4  # Create Error
        elif(cmd == 'dev'):
            if self.db.create_dev(payload) is not -1:
                valid = 0
            else:
                valid = 4  # Create Error
        response['valid'] = valid
        return response

    def __read(self, cmd, payload):
        '''
        Execute the Read commands, based on the cmd; Private access
        Params:
            cmd: Command to be executed, part of the original cmd passed
            payload: arguments passed along with the cmd, specific to the cmd.
        Returns: Response dict to be added as the response in the reply packet
        '''
        response = {'manifest': []}
        if(cmd == 'connman'):
            # Read Manifest of all connected devices
            # Query the network for currently connected items

            response['manifest'] = self.db.read_connman()
        elif(cmd == 'unconnman'):
            response['manifest'] = self.db.read_unconnman()
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

    def __update(self, cmd, payload):
        '''
        Execute the Update commands, based on the cmd; Private access
        Params:
            cmd: Command to be executed, part of the original cmd passed
            payload: arguments passed along with the cmd, specific to the cmd.
        Returns: Response dict to be added as the response in the reply packet
        '''
        response = payload
        if(cmd == 'grp'):
            return
        if(cmd == 'dev'):
            return
        if(cmd == 'devdata'):
            self.db.update_devdata(payload)
            return
        return response

    def __destroy(self, cmd, payload):
        '''
        Execute the Destroy commands, based on the cmd; Private access
        Params:
            cmd: Command to be executed, part of the original cmd passed
            payload: arguments passed along with the cmd, specific to the cmd.
        Returns: Response dict to be added as the response in the reply packet
        '''
        response = payload
        if(cmd == 'grp'):
            return
        elif(cmd == 'dev'):
            return
        return response
