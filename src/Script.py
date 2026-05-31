#!/usr/bin/env python3

# Script para configurar efectos de teclado Razer usando openrazer
# Se encargará de hacer pooling de los dispositivos y aplicar efectos automáticamente al detectar un nuevo dispositivo compatible

# Imports
import subprocess
import openrazer.client
import sys
import threading
import signal
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from pathlib import Path
# Cambia esto en tu línea 11
from openrazer.client.devices import RazerDevice

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from components.DeviceRegistry import DeviceRegistry
from src.components.SetupDevice import SetupDeviceManager


#Constantes
POLLING_INTERVAL = 3  # Intervalo de tiempo para hacer pooling de dispositivos (en segundos)
ALLOWED_DEVICE_TYPES = set(['keyboard', 'mouse'])  # Tipos de dispositivos a configurar



#Variables comunes

setup_devices_registry = DeviceRegistry()
setup_device_manager = SetupDeviceManager()
stop_event = threading.Event()



# Función para inicializar el DeviceManager y obtener los dispositivos compatibles
# El pooling se hace de forma constante par detectar nuevos dispositivos que se conecten después de iniciar el script


def is_device_active(device: RazerDevice):
    return 'v0.0' not in device.firmware_version  # Si el firmware es 0.0, el dispositivo no está activo

def is_device_usable(device: RazerDevice):
    """Verifica si el dispositivo está realmente disponible antes de usar."""
    try:
        # Intenta acceder a propiedades básicas para confirmar disponibilidad
        _ = device.firmware_version
        return 'v0.0' not in device.firmware_version
    except Exception as e:
        print(f"Dispositivo {device.name} no usable: {e}")
        return False

def poll_devices():
    try:
        device_manager: openrazer.client.DeviceManager = openrazer.client.DeviceManager()
        devices = [d for d in device_manager.devices 
                   if d.type in ALLOWED_DEVICE_TYPES and is_device_usable(d)]
        return devices
    
    except Exception as e:
        print(f"Error al obtener dispositivos: {e}")
        return []

def cleanup_disconnected_devices(devices: list[RazerDevice]):
    cleaned = False

    comparison = setup_devices_registry.compare_with_devices_list(devices)
    if len(comparison["removed"]) > 0:
        setup_devices_registry.clear_registry()  # Limpiar el registro de dispositivos configurados
        cleaned = True
           
    
    if cleaned:
        reload_open_razer_daemon()  #, requerido para detectar los cambios por defecto de deteccion en alternancia Wireless/USB
        stop_event.wait(3)  # Detener el script para reiniciarlo manualmente después de limpiar los dispositivos
        cleaned = False


def setup_connected_device(device: RazerDevice):
    if setup_devices_registry.is_device_registered(device):
        #print(f"El dispositivo {device.name} con PID {device._pid} ya está configurado, omitiendo...")
        return
    try:
        setup_device_manager.setup_device(device)
        setup_devices_registry.add_device(device)
    except Exception as e:
        print(f"Error al configurar el dispositivo {device.name} con PID {device._pid}: {e}")
    return
    
def clear_devices():
    for device in setup_devices_registry.get_registered_devices():
        try:
            setup_device_manager.unload_device(device)
        except Exception as e:
            print(f"Error al limpiar {device.name}: {e}")
    setup_devices_registry.clear_registry()

def reload_open_razer_daemon():
    print("Reiniciando openrazer daemon...")
    try:
        subprocess.run(['systemctl', '--user', 'restart', 'openrazer-daemon'], check=True)
        print("OpenRazer daemon reiniciado correctamente.")
    except Exception as e:
        print(f"Error al reiniciar openrazer-daemon: {e}")

def handle_stop_signal(signum, frame):
    signal_name = signal.Signals(signum).name
    print(f"Recibida señal {signal_name}. Deteniendo el script...")
    clear_devices()
    stop_event.set()


def handle_sleep_signal(sleeping: bool):
    """Maneja la señal de suspensión/reanudación del sistema."""
    if not sleeping:
        print("Sistema reanudado. Forzando limpieza y reconfiguración...")
        try:
            clear_devices()  # Limpiar cualquier dispositivo que pueda haber quedado en un estado inconsistente
            # El daemon de OpenRazer a veces pierde los dispositivos tras suspender
            reload_open_razer_daemon()
            print("OpenRazer daemon reiniciado tras reanudación.")
        except Exception as e:
            print(f"Error al reiniciar openrazer-daemon tras reanudación: {e}")
        setup_devices_registry.clear_registry()


def init_sleep_listener():
    """Inicializa el listener de DBus para eventos de suspensión."""
    try:
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        bus.add_signal_receiver(
            handle_sleep_signal,
            signal_name="PrepareForSleep",
            dbus_interface="org.freedesktop.login1.Manager",
            bus_name="org.freedesktop.login1"
        )
        
        def run_loop():
            loop = GLib.MainLoop()
            loop.run()
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        print("Listener de suspensión (DBus) iniciado correctamente.")
    except Exception as e:
        print(f"Advertencia: No se pudo configurar el listener de suspensión. {e}")

def handleStopSignal(signum, frame):
    signal_name = signal.Signals(signum).name
    print(f"Recibida señal {signal_name}. Deteniendo el script...")
    for device in setupDevices.values():
        try:
            unload_device(device)
        except Exception as e:
            print(f"Error al limpiar efectos del dispositivo {device.name} durante la detención: {e}")
    stop_event.set()


def main():
    signal.signal(signal.SIGINT, handle_stop_signal)
    signal.signal(signal.SIGTERM, handle_stop_signal)
    signal.signal(signal.SIGHUP, handle_stop_signal)
    signal.signal(signal.SIGQUIT, handle_stop_signal)

    init_sleep_listener()

    try:
        while not stop_event.is_set():
            devices = poll_devices()
            # Eliminar dispositivos que ya no están conectados
            cleanup_disconnected_devices(devices)
            for device in devices:
                setup_connected_device(device)
            stop_event.wait(POLLING_INTERVAL)
    except KeyboardInterrupt:
        print("Deteniendo el script...")
        stop_event.set()
    except Exception as e:
        print(f"Error inesperado: {e}")
        stop_event.set()                
main()













