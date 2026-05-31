# SetupDevice.py
from openrazer.client.devices import RazerDevice
from src.components.UserConfigRetriever import get_user_config
from src.models.ConfigModels import DeviceConfig, UserConfig
from src.components.Effects import apply_matrix_effects, cleanup_effects


class SetupDeviceManager:
    user_config: UserConfig | None

    def __init__(self):
        self.user_config = get_user_config()

    def apply_base_settings(self, device: RazerDevice, config: DeviceConfig | None):
        if config is not None:
            device.brightness = config.get("brightness", 100)

    def apply_settings(self, device: RazerDevice, config: DeviceConfig | None):
        self.apply_base_settings(device, config)
        apply_matrix_effects(device, config)

    def setup_device(self, device: RazerDevice):
        print(f"Configurando dispositivo {device.name} con PID {device._pid}...")
        user_config: UserConfig | None = self.user_config
        if user_config is None:
            print(f"No se pudo cargar la configuración para {device.name} con PID {device._pid}")
            return
        try:
            device_config = user_config.get(device.type)
            self.apply_settings(device, device_config)
        except Exception as e:
            print(f"Error al configurar el dispositivo {device.name} con PID {device._pid}: {e}")
            raise

    def unload_device(self, device: RazerDevice):
        try:
            cleanup_effects(device)
        except Exception as e:
            print(f"Error al limpiar efectos del dispositivo {device.name} durante la descarga: {e}")
