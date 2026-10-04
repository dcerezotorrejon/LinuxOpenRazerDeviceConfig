#!/usr/bin/env python3

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

INITIAL_DELAY = 3  # Tiempo inicial de espera antes de comenzar la configuración (en segundos)
POLLING_INTERVAL = 3  # Intervalo de tiempo para hacer pooling de dispositivos (en segundos)
ALLOWED_DEVICE_TYPES = {"keyboard", "mouse"}  # Tipos de dispositivos a configurar


class RazerScriptOrchestrator:
    def __init__(self, polling_interval: int = POLLING_INTERVAL):
        self.polling_interval = polling_interval
        self.stop_event = threading.Event()
        self._lock = threading.Lock()

        user_config = ConfigLoader().load()
        self.registry = DeviceRegistry()
        self.device_manager = SetupDeviceManager(user_config=user_config)
        self.device_poller = DevicePoller(allowed_types=ALLOWED_DEVICE_TYPES)

        self.signal_handler = SystemSignalHandler(on_stop=self.handle_stop_signal)
        self.sleep_listener = SystemSleepListener(on_sleep_event=self.handle_sleep_signal)

    def setup_connected_device(self, device: RazerDevice) -> None:
        with self._lock:
            if self.registry.is_device_registered(device):
                return
            try:
                self.device_manager.setup_device(device)
                self.registry.add_device(device)
            except Exception as e:
                print(f"Error al configurar el dispositivo {device.name} con PID {device._pid}: {e}")

    def clear_devices(self) -> None:
        with self._lock:
            for device in self.registry.get_registered_devices():
                try:
                    self.device_manager.unload_device(device)
                except Exception as e:
                    print(f"Error al limpiar {device.name}: {e}")
            self.registry.clear_registry()

    def cleanup_disconnected_devices(self, devices: list[RazerDevice]) -> None:
        with self._lock:
            comparison = self.registry.compare_with_devices_list(devices)
            if len(comparison["removed"]) == 0:
                return

            for device in comparison["removed"]:
                try:
                    self.device_manager.unload_device(device)
                    self.registry.remove_device(device)
                except Exception as e:
                    print(f"Error al limpiar dispositivo desconectado {device.name}: {e}")
            
            print(f"Limpiados {len(comparison['removed'])} dispositivo(s) desconectado(s).")

    def handle_stop_signal(self, signum: int, frame: object) -> None:
        signal_name = signal.Signals(signum).name
        print(f"Recibida señal {signal_name}. Deteniendo el script...")
        self.stop_event.set()

    def handle_sleep_signal(self, sleeping: bool) -> None:
        """Maneja la señal de suspensión/reanudación del sistema."""
        if sleeping:
            return

        print("Sistema reanudado. Forzando limpieza y reconfiguración...")
        try:
            self.clear_devices()
        except Exception as e:
            print(f"Error al limpiar dispositivos tras reanudación: {e}")

    def run(self) -> None:
        self.signal_handler.register_handlers()
        self.sleep_listener.start()

        if INITIAL_DELAY > 0:
            print(f"Esperando {INITIAL_DELAY}s antes de comenzar el sondeo...")
            self.stop_event.wait(INITIAL_DELAY)

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
        finally:
            print("Limpiando dispositivos antes de salir...")
            self.clear_devices()


def main():
    orchestrator = RazerScriptOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()

