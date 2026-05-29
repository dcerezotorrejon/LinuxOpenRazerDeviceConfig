#!/usr/bin/env python3

# Script para configurar efectos de teclado Razer usando openrazer
# Se encargará de hacer pooling de los dispositivos y aplicar efectos automáticamente al detectar un nuevo dispositivo compatible

# Imports
import subprocess
import openrazer.client
import sys
import threading
import signal
from pathlib import Path
# Cambia esto en tu línea 11
from openrazer.client.devices import RazerDevice

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.components.SetupDevice import setup_device, unload_device


#Constantes
POLLING_INTERVAL = 3  # Intervalo de tiempo para hacer pooling de dispositivos (en segundos)
ALLOWED_DEVICE_TYPES = set(['keyboard', 'mouse'])  # Tipos de dispositivos a configurar



#Variables comunes

setupDevices = dict[str, RazerDevice]()
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

def cleanupDevices(devices: list[RazerDevice]):
    cleaned = False

    for pid in list(setupDevices):
        if pid not in [d._pid for d in devices]:
            print(f"El dispositivo con PID {pid} ya no está conectado, eliminando de la configuración...")
            del setupDevices[pid]  # Eliminar el dispositivo de la lista de configurados
            cleaned = True
            break  # Salir del bucle después de limpiar, no es necesario seguir verificando
           
    
    if cleaned:
        print('Reiniciando openrazer daemon para refrescar la lista de dispositivos...')
        subprocess.run(['systemctl', '--user', 'restart', 'openrazer-daemon'], check=True)
        stop_event.wait(2)  # Detener el script para reiniciarlo manualmente después de limpiar los dispositivos
        cleaned = False


def setupDevice(device: RazerDevice):
    if device._pid in setupDevices:
        #print(f"El dispositivo {device.name} con PID {device._pid} ya está configurado, omitiendo...")
        return
    print(f"Configurando dispositivo {device.name} con PID {device._pid}...")
    setup_device(device)   
    setupDevices[device._pid] = device
    return
    

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
    signal.signal(signal.SIGINT, handleStopSignal)
    signal.signal(signal.SIGTERM, handleStopSignal)
    signal.signal(signal.SIGHUP, handleStopSignal)
    signal.signal(signal.SIGQUIT, handleStopSignal)

    try:
        while not stop_event.is_set():
            devices = pollDevices()
            # Eliminar dispositivos que ya no están conectados
            cleanupDevices(devices)
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













