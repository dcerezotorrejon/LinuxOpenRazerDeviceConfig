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
from src.components.SetupDevice import setup_device, unload_device


#Constantes
POLLING_INTERVAL = 3  # Intervalo de tiempo para hacer pooling de dispositivos (en segundos)
ALLOWED_DEVICE_TYPES = set(['keyboard', 'mouse'])  # Tipos de dispositivos a configurar



#Variables comunes

setupDevicesRegistry = DeviceRegistry()
stop_event = threading.Event()



# Función para inicializar el DeviceManager y obtener los dispositivos compatibles
# El pooling se hace de forma constante par detectar nuevos dispositivos que se conecten después de iniciar el script


def isDeviceActive(device: RazerDevice):
    return 'v0.0' not in device.firmware_version  # Si el firmware es 0.0, el dispositivo no está activo

def isDeviceUsable(device: RazerDevice):
    """Verifica si el dispositivo está realmente disponible antes de usar."""
    try:
        # Intenta acceder a propiedades básicas para confirmar disponibilidad
        _ = device.firmware_version
        return 'v0.0' not in device.firmware_version
    except Exception as e:
        print(f"Dispositivo {device.name} no usable: {e}")
        return False

def pollDevices():
    try:
        device_manager: openrazer.client.DeviceManager = openrazer.client.DeviceManager()
        devices = [d for d in device_manager.devices 
                   if d.type in ALLOWED_DEVICE_TYPES and isDeviceUsable(d)]
        return devices
    
    except Exception as e:
        print(f"Error al obtener dispositivos: {e}")
        return []

def cleanupDisconnectedDevices(devices: list[RazerDevice]):
    cleaned = False

    comparation = setupDevicesRegistry.compareWithDevicesList(devices)
    if len(comparation["removed"]) > 0:
        setupDevicesRegistry.clearRegistry()  # Limpiar el registro de dispositivos configurados
        cleaned = True
           
    
    if cleaned:
        reloadOpenRazerDaemon()  # Reiniciar el daemon para asegurarnos de que se liberen los recursos del dispositivo desconectado
        stop_event.wait(3)  # Detener el script para reiniciarlo manualmente después de limpiar los dispositivos
        cleaned = False


def setupDevice(device: RazerDevice):
    if setupDevicesRegistry.isDeviceRegistered(device):
        #print(f"El dispositivo {device.name} con PID {device._pid} ya está configurado, omitiendo...")
        return
    print(f"Configurando dispositivo {device.name} con PID {device._pid}...")
    setup_device(device)   
    setupDevicesRegistry.addDevice(device)
    return
    
def clearDevices():
    for device in setupDevicesRegistry.getRegisteredDevices():
        try:
            unload_device(device)
        except Exception as e:
            print(f"Error al limpiar {device.name}: {e}")
    setupDevicesRegistry.clearRegistry()

def reloadOpenRazerDaemon():
    print("Reiniciando openrazer daemon...")
    try:
        subprocess.run(['systemctl', '--user', 'restart', 'openrazer-daemon'], check=True)
        print("OpenRazer daemon reiniciado correctamente.")
    except Exception as e:
        print(f"Error al reiniciar openrazer-daemon: {e}")

def handleStopSignal(signum, frame):
    signal_name = signal.Signals(signum).name
    print(f"Recibida señal {signal_name}. Deteniendo el script...")
    clearDevices()
    stop_event.set()


def handleSleepSignal(sleeping: bool):
    """Maneja la señal de suspensión/reanudación del sistema."""
    if not sleeping:
        print("Sistema reanudado. Forzando limpieza y reconfiguración...")
        try:
            clearDevices()  # Limpiar cualquier dispositivo que pueda haber quedado en un estado inconsistente
            # El daemon de OpenRazer a veces pierde los dispositivos tras suspender
            reloadOpenRazerDaemon()
            print("OpenRazer daemon reiniciado tras reanudación.")
            stop_event.wait(2)# Esperar un momento para que el daemon se reinicie completamente
        except Exception as e:
            print(f"Error al reiniciar openrazer-daemon tras reanudación: {e}")
        setupDevicesRegistry.clearRegistry()


def initSleepListener():
    """Inicializa el listener de DBus para eventos de suspensión."""
    try:
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        bus.add_signal_receiver(
            handleSleepSignal,
            signal_name="PrepareForSleep",
            dbus_interface="org.freedesktop.login1.Manager",
            bus_name="org.freedesktop.login1"
        )
        
        def runLoop():
            loop = GLib.MainLoop()
            loop.run()
        
        thread = threading.Thread(target=runLoop, daemon=True)
        thread.start()
        print("Listener de suspensión (DBus) iniciado correctamente.")
    except Exception as e:
        print(f"Advertencia: No se pudo configurar el listener de suspensión. {e}")


def main():
    signal.signal(signal.SIGINT, handleStopSignal)
    signal.signal(signal.SIGTERM, handleStopSignal)
    signal.signal(signal.SIGHUP, handleStopSignal)
    signal.signal(signal.SIGQUIT, handleStopSignal)

    initSleepListener()

    try:
        while not stop_event.is_set():
            devices = pollDevices()
            # Eliminar dispositivos que ya no están conectados
            cleanupDisconnectedDevices(devices)
            for device in devices:
                setupDevice(device)
            stop_event.wait(POLLING_INTERVAL)
    except KeyboardInterrupt:
        print("Deteniendo el script...")
        stop_event.set()
    except Exception as e:
        print(f"Error inesperado: {e}")
        stop_event.set()                
main()













