from pydispatch import dispatcher
import socket
import time
# import os


class ZNetwork:
    # Wrapper for the gateway application
    # Not sure how this is going to work at the moment.
    # See the readme for more details

    def __init__(self, unconn_sig, val_sig):
        '''
        Initialize the Network
        Set up IPC and initialize the socket layer
        '''
        # Define Signals
        self.id_sig = "ZNetwork"
        self.update_devdata_sig = "update_devdata"
        self.update_commissions_sig = "update_commissions"
        self.update_unconn_signal = unconn_sig
        self.update_values = val_sig
        # Set up the Socket layer
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect('../servers/socket_IPC')
        # Connect up the signals to the listeners
        dispatcher.connect(
            self.update_devdata_listener,
            signal=self.update_devdata_sig,
            sender=dispatcher.Any
        )
        dispatcher.connect(
            self.update_commissions_listener,
            signal=self.update_commissions_sig,
            sender=dispatcher.Any
        )
        # Send a commission!
        self.update_commissions_listener(None)
        return

    def build_args(self, cmd, arg1, arg2='0'):
        '''
        Format the arguments of commands
        Parmas:
            cmd: Command to be sent
            arg1: first argument, often the only argument
            arg2: rarely used, defaults 0
        '''
        arg_switch = {
            'ON/OFF': {
                'arg1': str(int(arg1) & 0x01),
                'arg2': arg2
            },
            'LEVEL': {
                'arg1': str(int((arg1/10.0) * 0xFF)),
                'arg2': arg2
            }
        }
        return arg_switch.get(cmd)

    def build_command(self, cmd, ieee_addr='-1', arg1='0', arg2='0'):
        '''
        Encode the Commands for sending to the GW application
        params:
            cmd: Command to be executed, required
            ieee_addr: Unique Address identifier for the specific device
            arg1: First argument
            arg2: second argument, only used in some cases (Hue)
        '''
        cmd_switch = {
            'ON/OFF': '0',
            'LEVEL': '1',
            'HUE': '2',
            'SAT': '3',
            'PERMIT_JOIN': '4',
            'REMOVE': '5',
            'BIND': '6',
            'GROUP_ADD_REMOVE': '7',
            'QUIT': '10',
            'CLIENT_UPDATE': '11'
        }
        return '-'.join([ieee_addr, cmd_switch[cmd], arg1, arg2])

    def update_unconn_db(self, _manifest):
        '''
        Asynchronously update the database with a manifest of items in network
        Params:
            _manifest: manifest of all commissioned devices: list of dicts:
                ieee_addr: IEEE Address for identification purposes
                type: device type
        '''
        print "sending data to the DB for UNCONN"
        print "manifest = ", _manifest
        dispatcher.send(
            signal=self.update_unconn_signal,
            sender=self.id_sig,
            manifest=_manifest
        )
        return

    def update_values_db(self, _devdata):
        '''
        Send a signal to the Db to update the devdata values
        params:
            _devdata: Dict with fields:
                id
                error_code: returned from the network
                ctrl_type
                value
        '''
        dispatcher.send(
                signal=self.update_values,
                sender=self.id_sig,
                devdata=_devdata
                )
        return

    def update_devdata_listener(self, sender, device, control_data):
        '''
        Send the Update to devices
        Params:
            device: device id = ieee_addr
            control_data:
                type: type of control = boolean, gradient, status
                value: value to change to
        '''
        ctrl_type = control_data['type']
        ctrl_value = control_data['value']
        cmd = ''
        if ctrl_type == 'boolean':
            cmd = 'ON/OFF'
        elif ctrl_type == 'gradient':
            cmd = 'LEVEL'
        else:
            return  # poorly formatted
        args = self.build_args(cmd, ctrl_value)
        if args is None:
            return  # poorly formatted
        command = self.build_command(cmd, device, args['arg1'], args['arg2'])
        # Send off the command to the socket and wait
        # Potentially wait more than once: haven't fully tested.
        self.sock.send(command)
        message = self.sock.recv(1024)
        print message
        self.receive_non_commission_msg(message)
        # Send a commission request, because why not
        return

    def update_commissions_listener(self, sender):
        '''
        Listener for commissions Updates
        Connects to Socket layer to send a command to the Network
        '''
        # Call the commission update
        print "Updating Commissions"
        command_string = self.build_command('PERMIT_JOIN')
        print command_string
        # send off to the socket
        self.sock.send(command_string)
        join_confirm = self.sock.recv(1024)
        print join_confirm
        command_string = self.build_command('CLIENT_UPDATE')
        print command_string
        time.sleep(10)
        self.sock.send(command_string)
        message = self.sock.recv(1024)
        print message
        # Parse the received message
        items = message.split('|')
        if len(items) == 1:
            print "Router is off: canceling commission update"
            return  # Router is off
        endpoints = items[2:]  # Grab the relevant items
        ep_dict = []
        for ieee_id in endpoints:
            ep_dict.append({'ieee_addr': ieee_id})
        self.update_unconn_db(ep_dict)

    def receive_non_commission_msg(self, msg):
        '''
        Parse a message from the network that is not a commission
        NOTE: Commissions are handled seperately
        Params:
            msg: formatted string of a message from the Network
        '''
        fields = msg.split('|')
        msg_dict = {}
        for field in fields:
            kvp = field.split('=')
            msg_dict[kvp[0]] = kvp[1]
        cmd_name_sw = {
            '0006': 'ON/OFF',
            '0008': 'LEVEL'
        }
        # Get the cluster name to get the command name
        cmd_name = cmd_name_sw[msg_dict['clstr']]
        sent_value = int(msg_dict['val'], 16) & 0xFF
        valid = msg_dict['vld']
        dev_id = msg_dict['IEEE']
        type = ''
        if valid == 0:
            return  # Error: invalid
        if(cmd_name == 'ON/OFF'):
            type = 'boolean'
        elif(cmd_name == 'LEVEL'):
            type = 'gradient'
        self.update_values_db({
            'id': dev_id,
            'valid': valid,
            'value': sent_value,
            'ctrl_type': type
        })

        return
