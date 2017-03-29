from tinydb import TinyDB, where
from znetwork import ZNetwork
from pydispatch import dispatcher


class Database(object):
    '''
    Wrapper Class for the tinyDB functions
    Stores instances of the tables
    '''
    def __init__(self, dbStr):
        '''
        Initialize the tinyDB, the devTable, grpTable, and ctrlTable
        Params:
            dbStr: location of the tinyDB JSON file
        '''
        # Initialize the DB
        db = TinyDB(dbStr)
        self.devTable = db.table("devices")
        self.grpTable = db.table("groups")
        self.ctrlTable = db.table("controls")
        self.unconnTable = db.table("unconn")
        # Initialize the IPC for the network
        self.id_sig = "Database"
        self.unconn_sig = "unconn_db_sig"
        self.val_sig = "db_val_sig"
        dispatcher.connect(
                self.update_unconn_db,
                signal=self.unconn_sig,
                sender=dispatcher.Any)
        dispatcher.connect(
                self.update_dev_value,
                signal=self.val_sig,
                sender=dispatcher.Any)
        self.zn = ZNetwork(self.unconn_sig, self.val_sig)

    def update_unconn_db(self, sender, manifest):
        # Updating the database with the list of devices in the network
        print "Updating Unconn DB, inside db"
        db_dev_list = self.devTable.all()
        configured = []
        unconfigured = []
        removed = []
        for db_dev in db_dev_list:
            matched = False
            for net_dev in manifest:
                # Attempt to match the ids
                if net_dev['ieee_addr'] == db_dev['id']:
                    # Match found
                    matched = True
                    configured.append(db_dev)
                    db_dev_list.remove(db_dev)
                    manifest.remove(net_dev)
                    break
            if matched:
                break
            else:
                # dev not found
                removed.append(db_dev)
                db_dev_list.remove(db_dev)
        # What is left in the manifest is the unconfigured list
        unconfigured = manifest

        # Update unconnTable
        for dev in unconfigured:
            # Check if already in table
            # if already in table, ignore.
            # else, insert
            id = dev['ieee_addr']
            if self.unconnTable.get(where('ieee_addr') == id) is None:
                    self.unconnTable.insert(dev)

        # Update the devTable
        for dev in removed:
            self.destroy_dev({
                'grp_name': dev['grp_name'],
                'dev_name': dev['name']
                })
        return

    def update_dev_value(self, sender, devdata):
        '''
        Update the values of the controls in a given control
        May or may not be necessary; used for response to an update_devdata
        '''
        # unpack the Dict
        # dev_id = devdata['id']
        # valid = devdata['valid']
        # ctrl_type = devdata['ctrl_type']
        # value = devdata['value']
        return

    def send_commission_request(self):
        print "Sending  Commission Request to the ZNetwork"
        dispatcher.send(
            signal=self.zn.update_commissions_sig,
            sender=self.id_sig
        )

    # CREATE
    def create_grp(self, grp_name):
        '''
        Create a group with the provided Group Name
        Return the Group's EID (entry id)

        Params:
            grp_name: Name of the group to be created
        '''
        if self.grpTable.get(where('grp_name') == grp_name) is not None:
            return -1
        try:
            grp_eid = self.grpTable.insert({
                'grp_name': grp_name
                })
        except:
            return -1  # Error
        return grp_eid

    def create_dev(self, payload):
        '''
        Add a device with a payload Dict.
        Return the EID (entry id)
        Params:
            payload: Dict = {
                grp_name: Group Name,
                dev_name: Device Name,
                dev_id: Device ID (IEEE),
                type: Device Type,
                controls: [{
                    name: Control Name,
                    type: Control Type (bool, gradient, status),
                    (value: Control value, optional) = 0 if None
                }]
            }
        '''
        # Unpack the Dict
        grp = payload['grp_name']
        dev = payload['dev_name']
        type = payload['type']
        id = payload['dev_id']
        ctrls = payload['controls']
        if self.grpTable.get(where('grp_name') == grp) is None:
            return -1
        if self.devTable.get(
                (where('grp_name') == grp) &
                (where('dev_name') == dev)) is not None:
            return -1
        # Search the unconnTable for the device, and pop it out
        unconn_dev = self.unconnTable.get(where('ieee_addr') == id)
        if unconn_dev is None:
            # error
            print "Error: unfound in table"
            return -1
        self.unconnTable.remove(unconn_dev.eid)

        dev_eid = self.devTable.insert({
            'name': dev,
            'grp_name': grp,
            'id': id,
            'type': type
            })
        for ctrl in ctrls:
            self.ctrlTable.insert({
                'name': ctrl['name'],
                'type': ctrl['type'],
                'value': ctrl.get('value', None),
                'dev_name': dev,
                'grp_name': grp
                })
        return dev_eid

    # READ
    def read_grpman(self):
        '''
        Return the Manifest of all groups currently in the DB
        '''
        print "Read Grpman"
        return self.grpTable.all()

    def read_devman(self, group_name):
        '''
        Return all devices that match a given group

        Params:
            group_name: name of the devices' parent group
        '''
        return self.devTable.search(where('grp_name') == group_name)

    def read_ctrlman(self, group, device):
        # Returns all controls associated with a given device in a given group
        return self.ctrlTable.search(
                (where('dev_name') == device) &
                (where('grp_name') == group)
               )

    def read_connman(self):
        '''
        Return list of all devices available on the network and also in the db
        '''
        db_manifest = []
        groups = self.grpTable.all()
        for group in groups:
            print group
            grpDict = {}
            grpDict['grp_name'] = group['grp_name']
            grpDict['devices'] = self.read_devman(group['grp_name'])
            for dev in grpDict['devices']:
                print dev
                ctrls = self.read_ctrlman(group['grp_name'], dev['name'])
                print ctrls
                dev['controls'] = ctrls
            db_manifest.append(grpDict)
        # Begin a commission
        self.send_commission_request
        return db_manifest

    def read_unconnman(self):
        '''
        Return the manifest of all devices that are available on
        the network, but not in the db
        '''
        unconn_manifest = []
        unconns = self.unconnTable.all()
        print "Printing the unconns:", unconns
        for unconn in unconns:
            print unconn
            ucDict = {
                    'id': unconn.get('ieee_addr'),
                    'type': unconn.get('type', None)
                    }
            unconn_manifest.append(ucDict)
        print unconn_manifest
        return unconn_manifest

    # UPDATE
    def update_devdata(self, payload):
        # assume that payload is a Dict, received from the WC
        grp = payload['grp_name']
        dev = payload['dev_name']
        ctrl = payload['ctrl_name']
        new_name = payload.get('name', None)  # Optional argument: else None
        new_value = payload.get('value', None)  # Optional argument: else None

        # find the control itself:
        device_id = self.devTable.get(
            (where('name') == dev) &
            (where('grp_name') == grp))['id']

        control = self.ctrlTable.get(
            (where('grp_name') == grp) &
            (where('dev_name') == dev) &
            (where('name') == ctrl))

        # Send a update to the network
        dispatcher.send(
            signal=self.zn.update_devdata_sig,
            sender=self.id_sig,
            device=device_id,
            control_data={
                'type': control.type,
                'value': new_value
            }
        )
        if new_name is not None:
            ctrl_eids = self.ctrlTable.update(
                {'name': new_name}, control.eid)
        if new_value is not None:
            ctrl_eids = self.ctrlTable.update(
                {'value': new_value}, control.eid)

        if ctrl_eids == []:
            return -1
        else:
            return ctrl_eids[0]

    # update_dev & update_grp

    # DESTROY
    def destroy_grp(self, grp_name):
        '''
        Remove a group, and any devices and controls associated with it
        '''
        # use remove() to delete an element
        # make sure to delete all ctrls and devices asociated, recursively
        target_grp = self.grpTable.get(where('grp_name') == grp_name)

        assoc_devices = self.devTable.search(where('grp_name') == grp_name)
        assoc_ctrls = self.ctrlTable.search(where('grp_name') == grp_name)
        for ctrl in assoc_ctrls:
            self.ctrlTable.remove(ctrl.eid)
        for dev in assoc_devices:
            self.devTable.remove(dev.eid)
        self.grpTable.remove(target_grp.eid)
        # Remove from the network? => send a decommission request
        return

    def destroy_dev(self, payload):
        '''
        Remove a device, and all controls associated with it from the table
        '''
        dev_name = payload['dev_name']
        grp_name = payload['grp_name']
        target_dev = self.devTable.get(
                (where('name') == dev_name) &
                (where('grp_name') == grp_name))
        assoc_ctrls = self.ctrlTable.search(
                (where('dev_name') == dev_name) &
                (where('grp_name') == grp_name))
        for ctrl in assoc_ctrls:
            self.ctrlTable.remove(ctrl.eid)
        self.devTable.remove(target_dev.eid)
        # Remove from the network?
        return
