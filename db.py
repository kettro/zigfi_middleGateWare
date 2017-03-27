from tinydb import TinyDB, Query, where
from znetwork import ZNetwork as zn

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
        db = TinyDB(dbStr)
        self.devTable = db.table("devices")
        self.grpTable = db.table("groups")
        self.ctrlTable = db.table("controls")

    '''
    NOTE:
    Assume that all actions are already valid
    Assume all functions are after receiving information from the network
    get all devices that are members of a supplied group
    '''
    #CREATE
    def create_grp(self, grp_name):
        '''
        Create a group with the provided Group Name
        Return the Group's EID (entry id)

        Params:
            grp_name: Name of the group to be created
        '''
        if self.grpTable.get(where('grp_name') == grp) is not None:
            return -1
        try:
            grp_eid = self.grpTable.insert({
                'grp_name': grp_name
                })
        except:
            return -1 # Error
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
        # search the network for the device and get info on it
        #TODO: insert the devdata into the devTable
        #TODO: return error if no dev is found with that ieee address

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
                'value': ctrl['value'],
                'dev_name': dev,
                'grp_name': grp
                })
        return dev_eid

    # READ
    def read_grpman(self):
        '''
        Return the Manifest of all groups currently in the DB
        '''
        return self.grpTable.all()

    def read_devman(self, group_name):
        '''
        Return all devices that match a given group

        Params:
            group_name: name of the devices' parent group
        '''
        return self.devTable.search(where('grp_name') == group_name)

    # Returns all controls associated with a given device in a given group
    def read_ctrlman(self, group, device):
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
        #TODO: Begin a commission
        return db_manifest

    def read_unconnman(self):
        '''
        Return the manifest of all devices that are available on
        the network, but not in the db
        '''
        manifests = self.read_network_manifests()
        return manifests['new_nodes']

    def read_network_manifests(self):
        zn_manifest = self.zn.read_manifest()
        db_manifest = []
        groups = self.grpTable.all()
        for group in groups:
            grpDict = {}
            grpDict['grp_name'] = group['grp_name']
            grpDict['devices'] = self.read_devman(group['grp_name'])
            for dev in grpDict['devices']:
                ctrls = self.read_ctrlman(group['grp_name'], dev['name'])
                dev['controls'] = ctrls
            db_manifest.push(grpDict)
        # Check whether the devices in the db are still on the network
        unconnected = []
        connected = []
        for grouping in db_manifest:
            for device in grouping:
                # for each device in the db
                # Check if it is in the network too
                for node in zn_manifest:
                    # Check each node in the network
                    if(node['ieee_id'] == device['id']):
                        # If they have matching ieee ids, then they are the same
                        # Remove the node from the zn manifest, for faster searching
                        #TODO: set the value of the controls of the device
                        zn_manifest.remove(node)
                        connected.append(device)
                if(connected.count(device) is 0):
                    # The device was not found in the network
                    unconnected.append(device)
        # connected for connman, zn_manifest for unconnman
        manifests = {
                'connected': connected,
                'unconnected': unconnected,
                'new_nodes': zn_manifest
                }
        return manifests

    # UPDATE
    def update_devdata(self, payload):
        #assume that payload is a Dict, received from the WC
        response = {}
        grp = payload['grp_name']
        dev = payload['dev_name']
        ctrl = payload['ctrl_name']
        new_name = payload['name']
        new_value = payload['value']

        #find the control itself:
        device_id = devTable.get(
                (where('name') == dev) &
                (where('grp_name') == grp))['id']
        updated_ctrl_value = zn.update_devdata(device_id, ctrl)
        Ctrl = Query()
        control = ctrlTable.get(
                (Ctrl.grp_name == grp) &
                (Ctrl.dev_name == dev) &
                (Ctrl.name==ctrl)
                )
        # TODO: put the data retrieved from the network in the db, not the passed values
        control['name'] = new_name
        control['value'] = new_value
        return control

    # DESTROY
    def destroy_grp(self, grp_name):
        '''
        Remove a group, and any devices and controls associated with it
        '''
        # use remove() to delete an element
        # make sure to delete all ctrls and devices asociated, recursively
        target_grp = grpTable.get(where('grp_name') == grp_name)

        assoc_devices = devTable.search(where('grp_name') == grp_name)
        assoc_ctrls = ctrlTable.search(where('grp_name') == grp_name)
        for ctrl in assoc_ctrls:
            ctrlTable.remove(ctrl.eid)
        for dev in assoc_devices:
            devTable.remove(dev.eid)
        grpTable.remove(target_grp.eid)
        # Remove from the network? => send a decommission request
        return

    def destroy_dev(self, payload):
        '''
        Remove a device, and all controls associated with it from the table
        '''
        dev_name = payload['dev_name']
        grp_name = payload['grp_name']
        target_dev = devTable.get(
                (where('name') == dev_name) &
                (where('grp_name') == grp_name))
        assoc_ctrls = ctrlTable.search(
                (where('dev_name') == dev_name) &
                (where('grp_name') == grp_name))
        for ctrl in assoc_ctrls:
            ctrlTable.remove(ctrl.eid)
        devTable.remove(target_dev.eid)
        # Remove from the network?
        return

    # get all groups currently registered

    # get all controls for a given device

