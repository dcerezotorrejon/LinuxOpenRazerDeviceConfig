#!/usr/bin/env python3

import subprocess
import sys
import threading
import signal
from pathlib import Path

from openrazer.client.devices import RazerDevice

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.components.DevicePoller import DevicePoller
from src.components.DeviceRegistry import DeviceRegistry
from src.components.SystemEvents import SystemSignalHandler, SystemSleepListener
from src.components.SetupDevice import SetupDeviceManager
from src.components.UserConfigRetriever import ConfigLoader


POLLING_INTERVAL = 3  # Intervalo de tiempo para hacer pooling de dispositivos (en segundos)
ALLOWED_DEVICE_TYPES = {"keyboard", "mouse"}  # Tipos de dispositivos a configurar


class RazerScriptOrchestrator:
    def __init__(self, polling_interval: int = POLLING_INTERVAL):
        self.polling_interval = polling_interval
        self.stop_event = threading.Event()

        user_config = ConfigLoader().load()
        self.registry = DeviceRegistry()
        self.device_manager = SetupDeviceManager(user_config=user_config)
        self.device_poller = DevicePoller(allowed_types=ALLOWED_DEVICE_TYPES)

        self.signal_handler = SystemSignalHandler(on_stop=self.handle_stop_signal)
        self.sleep_listener = SystemSleepListener(on_sleep_event=self.handle_sleep_signal)

    def reload_open_razer_daemon(self) -> None:
        print("Reiniciando openrazer daemon...")
        try:
            subprocess.run(["systemctl", "--user", "restart", "openrazer-daemon"], check=True)
            print("OpenRazer daemon reiniciado correctamente.")
        except Exception as e:
            print(f"Error al reiniciar openrazer-daemon: {e}")

    def setup_connected_device(self, device: RazerDevice) -> None:
        if self.registry.is_device_registered(device):
            return
        try:
            self.device_manager.setup_device(device)
            self.registry.add_device(device)
        except Exception as e:
            print(f"Error al configurar el dispositivo {device.name} con PID {device._pid}: {e}")

    def clear_devices(self) -> None:
        for device in self.registry.get_registered_devices():
            try:
                self.device_manager.unload_device(device)
            except Exception as e:
                print(f"Error al limpiar {device.name}: {e}")
        self.registry.clear_registry()

    def cleanup_disconnected_devices(self, devices: list[RazerDevice]) -> None:
        comparison = self.registry.compare_with_devices_list(devices)
        if len(comparison["removed"]) == 0:
            return

        self.registry.clear_registry()
        # Requerido para detectar cambios por alternancia Wireless/USB.
        self.reload_open_razer_daemon()
        self.stop_event.wait(3)

    def handle_stop_signal(self, signum: int, frame: object) -> None:
        signal_name = signal.Signals(signum).name
        print(f"Recibida señal {signal_name}. Deteniendo el script...")
        self.clear_devices()
        self.stop_event.set()

    def handle_sleep_signal(self, sleeping: bool) -> None:
        """Maneja la señal de suspensión/reanudación del sistema."""
        if sleeping:
            return

        print("Sistema reanudado. Forzando limpieza y reconfiguración...")
        try:
            # Limpiar dispositivos que pueden quedar en estado inconsistente.
            self.clear_devices()
            self.reload_open_razer_daemon()
            print("OpenRazer daemon reiniciado tras reanudación.")
        except Exception as e:
            print(f"Error al reiniciar openrazer-daemon tras reanudación: {e}")
        self.registry.clear_registry()

    def run(self) -> None:
        self.signal_handler.register_handlers()
        self.sleep_listener.start()

        try:
            while not self.stop_event.is_set():
                devices = self.device_poller.poll_devices()
                self.cleanup_disconnected_devices(devices)
                for device in devices:
                    self.setup_connected_device(device)
                self.stop_event.wait(self.polling_interval)
        except KeyboardInterrupt:
            print("Deteniendo el script...")
            self.stop_event.set()
        except Exception as e:
            print(f"Error inesperado: {e}")
            self.stop_event.set()


def main():
    orchestrator = RazerScriptOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()













