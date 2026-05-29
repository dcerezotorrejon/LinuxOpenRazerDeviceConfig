from openrazer.client.devices import RazerDevice

from models.ConfigModels import DeviceConfig

def apply_matrix_effects(device: RazerDevice, config: DeviceConfig | None):
    try:
        if config is None:
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

def cleanup_effects(device: RazerDevice):
    try:
        if device.capabilities.get('lighting_led_matrix') is not True:
            return 
        
        device.fx.none()
    except Exception as e:
        print(f"Error al limpiar efectos del dispositivo {device.name}")
        print(f"Detalles del error: \n {e}")