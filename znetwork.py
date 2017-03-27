from pydispatch import dispatcher

class ZNetwork:
    # Wrapper for the gateway application
    # Not sure how this is going to work at the moment.
    # See the readme for more details

    def __init__(self, unconn_sig, val_sig):
        self.id_sig = "ZNetwork"
        self.update_devdata_sig = "update_devdata"
        self.update_unconn_signal = unconn_sig
        self.update_values = val_sig
        dispatcher.connect(
                self.update_devdata_listener,
                signal=self.update_devdata_sig,
                sender=dispatcher.Any)
        return

    def update_unconn_db(self, _manifest):
        '''
        Asynchronously update the database with the manifest of items in the network
        Params:
            _manifest: manifest of all commissioned devices: list of dicts with the fields:
                ieee_addr: IEEE Address for identification purposes
                type: device type
        '''
        dispatcher.send(
                signal=self.update_unconn_signal,
                sender=self.id_sig,
                manifest=_manifest
                )
        return

    def update_values_db(self, _devdata):
        '''
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
        return

    def read_devdata(self, ieee_addr):
        # supposed to take the ieee_addr and return all the devdata associated in a Dict
        return

    def update_devdata(self, ieee_addr, controlDict):
        # Update the value of a control of a specified device, by ieee_addr & control type
        # Return a confirmation...? Or the current value of that device?
        return

    def read_manifest(self, update):
        manifest = []
        # Return the manifest of the network
        # update: whether or not to request an update on the network
        return manifest
