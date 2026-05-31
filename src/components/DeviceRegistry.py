from openrazer.client.devices import RazerDevice

class DeviceRegistry:
    devices: dict[str, RazerDevice]

    def __init__(self):
        self.devices = dict[str, RazerDevice]()
    
    def addDevice(self, device: RazerDevice):
        self.devices[device.name] = device

    def isDeviceRegistered(self, device: RazerDevice):
        return device.name in self.devices 
    
    def clearRegistry(self):
        self.devices.clear()
    def getRegisteredDevices(self):
        return list(self.devices.values())

    def compareWithDevicesList(self, devices: list[RazerDevice]):
        added: list[RazerDevice] = []
        removed: list[RazerDevice] = []

        current_device_names = set(self.devices.keys())
        new_device_names = set(d.name for d in devices)

        for device in devices:
            if device.name not in current_device_names:
                added.append(device)

        for name in current_device_names:
            if name not in new_device_names:
                removed.append(self.devices[name])

        return {"added": added, "removed": removed}
