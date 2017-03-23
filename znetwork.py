class ZNetwork:
    # Wrapper for the gateway application
    # Not sure how this is going to work at the moment.
    # See the readme for more details

    @staticmethod
    def read_devdata(ieee_addr):
        # supposed to take the ieee_addr and return all the devdata associated in a Dict
        return

    @staticmethod
    def update_devdata(ieee_addr, controlDict):
        # Update the value of a control of a specified device, by ieee_addr and control type
        # Return a confirmation...? Or the current value of that device?
        return

    @staticmethod
    def read_manifest(update):
        manifest = []
        # Return the manifest of the network
        # update: whether or not to request an update on the network
        return manifest
