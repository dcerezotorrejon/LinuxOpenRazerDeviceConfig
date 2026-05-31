from openrazer.client import DeviceManager
from openrazer.client.devices import RazerDevice


class DevicePoller:
    def __init__(self, allowed_types: set[str]):
        self.allowed_types = allowed_types

    def is_device_usable(self, device: RazerDevice) -> bool:
        """Verifica si el dispositivo esta realmente disponible antes de usar."""
        try:
            firmware_version = device.firmware_version
            return "v0.0" not in firmware_version
        except Exception as e:
            print(f"Dispositivo {device.name} no usable: {e}")
            return False

    def poll_devices(self) -> list[RazerDevice]:
        try:
            device_manager: DeviceManager = DeviceManager()
            return [
                device
                for device in device_manager.devices
                if device.type in self.allowed_types and self.is_device_usable(device)
            ]
        except Exception as e:
            print(f"Error al obtener dispositivos: {e}")
            return []
