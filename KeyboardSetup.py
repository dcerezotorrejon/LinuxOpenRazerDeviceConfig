# KeyboardSetup.py

# Cambia esto en tu línea 11
import json
import os
from openrazer.client.devices import RazerDevice

CONFIG_PATH = "~/Scripts/Razer/KeyboardConfig.json"
_CONFIG_CACHE = None

def load_keyboard_config(config_path=CONFIG_PATH, force_reload=False):
    """Carga el archivo JSON de configuración."""
    global _CONFIG_CACHE
    if not force_reload and _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = os.path.expanduser(config_path)
    try:
        with open(config_path, "r", encoding="utf-8") as archivo:
            _CONFIG_CACHE = json.load(archivo) or dict()
            return _CONFIG_CACHE
    except Exception as e:
        print(f"Error al cargar el archivo de configuración: {e}")
        return None

def apply_effects(device: RazerDevice):
    try:
        config = load_keyboard_config()
        if config is None:
            print("No se pudo cargar la configuración, aplicando efectos por defecto...")
            return

        if device.capabilities.get('lighting_led_matrix') is not True:
            return 
        
        rows = device.fx.advanced.matrix._rows
        cols = device.fx.advanced.matrix._cols

        default_color = config.get("default_color", [0, 0, 0]);
        custom_keys = config.get("custom_keys", dict()) 


        for r in range(rows):
            for c in range(cols):
                custom_config = custom_keys.get(str(r), {}).get(str(c), None)
                current_color = custom_config["color"] if custom_config is not None else default_color
                device.fx.advanced.matrix.set(r, c, tuple(current_color))
            
   

        device.fx.advanced.draw()
    except Exception as e:
        print(f"Error al aplicar efectos al dispositivo {device.name}")
        print(f"Detalles del error: \n {e}")

def apply_configurations(device: RazerDevice):
    config = load_keyboard_config()
    if config is not None:
        device.brightness = config.get("brightness", 50)


def setup(device: RazerDevice):
    apply_configurations(device)
    apply_effects(device)

load_keyboard_config.cache_config = None