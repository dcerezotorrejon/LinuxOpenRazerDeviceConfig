# SetupDevice.py
from openrazer.client.devices import RazerDevice
from src.components.UserConfigRetriever import getUserConfig
from src.models.ConfigModels import DeviceConfig, UserConfig
from src.components.Effects import applyMatrixEffects, cleanupEffects


class SetupDeviceManager:
    def applyBaseSettings(self, device: RazerDevice, config: DeviceConfig | None):
        if config is not None:
            device.brightness = config.get("brightness", 100)

    def applySettings(self, device: RazerDevice, config: DeviceConfig | None):
        self.applyBaseSettings(device, config)
        applyMatrixEffects(device, config)

    def setupDevice(self, device: RazerDevice):
        print(f"Configurando dispositivo {device.name} con PID {device._pid}...")
        user_config: UserConfig | None = getUserConfig()
        if user_config is None:
            print(f"No se pudo cargar la configuración para {device.name} con PID {device._pid}")
            return
        try:
            device_config = user_config.get(device.type)
            self.applySettings(device, device_config)
        except Exception as e:
            print(f"Error al configurar el dispositivo {device.name} con PID {device._pid}: {e}")
            raise e

    def unloadDevice(self, device: RazerDevice):
        try:
            cleanupEffects(device)
        except Exception as e:
            print(f"Error al limpiar efectos del dispositivo {device.name} durante la descarga: {e}")
