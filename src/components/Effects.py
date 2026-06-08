from openrazer.client.devices import RazerDevice

from src.models.ConfigModels import DeviceConfig

class EffectsManager:
    def apply_matrix_effects(self, device: RazerDevice, config: DeviceConfig | None) -> None:
        try:
            if config is None:
                return

            default_color = tuple(config.get("default_color", [255, 255, 255]))

            if device.capabilities.get("lighting_led_matrix") is not True:
                print(
                    f"El dispositivo {device.name} no tiene matriz de LEDs, aplicando efecto estático con el color por defecto."
                )
                # Fallback para dispositivos (p. ej. algunos mouse) sin matriz expuesta.
                if hasattr(device.fx, "static"):
                    device.fx.static(*default_color)
                return

            rows = device.fx.advanced.rows
            cols = device.fx.advanced.cols

            default_color = config.get("default_color", [255, 255, 255])
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

    def cleanup_effects(self, device: RazerDevice) -> None:
        try:
            if hasattr(device.fx, "none"):
                device.fx.none()
        except Exception as e:
            print(f"Error al limpiar efectos del dispositivo {device.name}")
            print(f"Detalles del error: \n {e}")