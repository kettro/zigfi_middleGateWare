from tinydb import TinyDB, Query, where

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
        devTable = db.table("devices")
        grpTable = db.table("groups")
        ctrlTable = db.table("controls")

    '''
    NOTE:
    Assume that all actions are already valid
    Assume all functions are after receiving information from the network
    get all devices that are members of a supplied group
    '''
    #CREATE
    def create_grp(grp_name):
        '''
        Create a group with the provided Group Name
        Return the Group's EID (entry id)

        Params:
            grp_name: Name of the group to be created
        '''
        return grpTable.insert({
            'grp_name': grp_name
            })

    def create_dev(payload):
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
        value = 0 # provide scope
        if payload['value'] is not None: value = payload['value']

        dev_eid = devTable.insert({
            'name': dev,
            'grp_name': grp,
            'id': id,
            'type': type
            })
        for ctrl in ctrls:
            ctrlTable.insert({
                'name': ctrl['name'],
                'type': ctrl['type'],
                value: value,
                'dev_name': dev,
                'grp_name': grp
                })
        return dev_eid

    # READ
    def read_devman(group_name):
        '''
        Return all devices that match a given group

        Params:
            group_name: name of the devices' parent group
        '''
        return devTable.search(where('grp_name') == group_name)

    # Returns all controls associated with a given device in a given group
    def read_ctrlman(group, device):
        Control = Query()
        return ctrlTable.search(
                Control.dev_name == device &
                Control.grp_name = group
               )


    # Returns the manifest of all devices inside groups connected
    def read_connman():
        manifest = []
        groups = grpTable.all()
        for group in groups:
            grpDict = {}
            grpDict['grp_name'] = group['grp_name']
            grpDict['devices'] = read_devman(group['grp_name'])
            for dev in grpDict['devices']:
                ctrls = read_ctrlman(group['grp_name'], dev['name'])
                dev['controls'] = ctrls
            manifest.push(grpDict)
        return manifest

    # UPDATE
    def update_devdata(payload):
        #assume that payload is a Dict, received from the WC
        response = {}
        grp = payload['grp_name']
        dev = payload['dev_name']
        ctrl = payload['ctrl_name']
        new_name = payload['name']
        new_value = payload['value']

        #find the control itself:
        #def updateDevData(name, value):
        #    def op(element):
        #        element['name'] = name
        #        element['value'] = value
        #    return op

        #ctrlTable.update(updateDevData(new_name, new_value), (Ctrl.grp_name==grp_name) & (Ctrl.dev_name==dev_name) & (Ctrl.name==ctrl_name))
        #Or::
        Ctrl = Query()
        control = ctrlTable.get(
                (Ctrl.grp_name==grp) &
                (Ctrl.dev_name==dev) &
                (Ctrl.name==ctrl)
                )
        control['name'] = new_name
        control['value'] = new_value
        return control



    # DESTROY





    # get all groups currently registered

    # get all controls for a given device

