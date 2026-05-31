from openrazer.client.devices import RazerDevice

class DeviceRegistry:
    devices: dict[str, RazerDevice]

    def __init__(self):
        self.devices = dict[str, RazerDevice]()
    
    def add_device(self, device: RazerDevice):
        self.devices[device.name] = device

    def is_device_registered(self, device: RazerDevice):
        return device.name in self.devices 
    
    def clear_registry(self):
        self.devices.clear()

    def get_registered_devices(self):
        return list(self.devices.values())

    def compare_with_devices_list(self, devices: list[RazerDevice]):
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
