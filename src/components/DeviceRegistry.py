from typing import Callable

from openrazer.client.devices import RazerDevice


class DeviceRegistry:
    devices: dict[str, RazerDevice]
    _on_add: list[Callable[[RazerDevice], None]]
    _on_remove: list[Callable[[RazerDevice], None]]

    def __init__(self):
        self.devices = dict[str, RazerDevice]()
        self._on_add = []
        self._on_remove = []

    @staticmethod
    def _device_key(device: RazerDevice) -> str:
        serial = getattr(device, "serial", None) or getattr(device, "serial_number", None)
        if serial and str(serial).strip():
            return str(serial)
        pid = getattr(device, "_pid", None)
        product_id = getattr(device, "product_id", None)
        if pid is not None or product_id is not None:
            return f"{device.name}:{pid or product_id}"
        return device.name

    def add_device(self, device: RazerDevice):
        key = self._device_key(device)
        already = key in self.devices
        self.devices[key] = device
        if not already:
            for cb in self._on_add:
                try:
                    cb(device)
                except Exception:
                    pass

    def is_device_registered(self, device: RazerDevice):
        return self._device_key(device) in self.devices

    def remove_device(self, device: RazerDevice):
        key = self._device_key(device)
        removed = self.devices.pop(key, None)
        if removed is not None:
            for cb in self._on_remove:
                try:
                    cb(device)
                except Exception:
                    pass
        return removed is not None

    def clear_registry(self):
        removed = list(self.devices.values())
        self.devices.clear()
        for device in removed:
            for cb in self._on_remove:
                try:
                    cb(device)
                except Exception:
                    pass

    def get_registered_devices(self):
        return list(self.devices.values())

    def compare_with_devices_list(self, devices: list[RazerDevice]):
        added: list[RazerDevice] = []
        removed: list[RazerDevice] = []

        current_keys = set(self.devices.keys())
        new_keys: dict[str, RazerDevice] = {}
        for d in devices:
            k = self._device_key(d)
            new_keys[k] = d

        for k, d in new_keys.items():
            if k not in current_keys:
                added.append(d)

        for k in current_keys:
            if k not in new_keys:
                removed.append(self.devices[k])

        return {"added": added, "removed": removed}

    def add_callback(self, event: str, callback: Callable[[RazerDevice], None]):
        if event == "add":
            self._on_add.append(callback)
        elif event == "remove":
            self._on_remove.append(callback)
        else:
            raise ValueError(f"Evento no soportado: {event}")
