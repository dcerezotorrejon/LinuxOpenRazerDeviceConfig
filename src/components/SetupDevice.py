# SetupDevice.py
from openrazer.client.devices import RazerDevice
from src.components.UserConfigRetriever import get_user_config
from src.models.ConfigModels import DeviceConfig, UserConfig
from src.components.Effects import apply_matrix_effects



def apply_base_settings(device: RazerDevice, config: DeviceConfig | None):
    if config is not None:
        device.brightness = config.get("brightness", 100)


def apply_settings(device: RazerDevice, config: DeviceConfig | None):
    apply_base_settings(device, config)
    apply_matrix_effects(device, config)



def setup_device(device: RazerDevice):
    user_config: UserConfig | None = get_user_config()
    if user_config is None:
        print(f"No se pudo cargar la configuración para {device.name} con PID {device._pid}")
        return
    try:
        device_config = user_config.get(device.type)
        apply_settings(device, device_config)
    except Exception as e:
        print(f"Error al configurar el dispositivo {device.name} con PID {device._pid}: {e}")


      