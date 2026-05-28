#!/usr/bin/env python3

# Script para configurar efectos de teclado Razer usando openrazer
# Se encargará de hacer pooling de los dispositivos y aplicar efectos automáticamente al detectar un nuevo dispositivo compatible

# Imports
import subprocess  
import importlib.util
import openrazer.client
import time
from pathlib import Path
# Cambia esto en tu línea 11
from openrazer.client.devices import RazerDevice



def _load_keyboard_setup():
    module_path = Path(__file__).with_name("KeyboardSetup.py")
    spec = importlib.util.spec_from_file_location("KeyboardSetup", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo desde {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.setup


setup_keyboard = _load_keyboard_setup()

#Constantes
POLLING_INTERVAL = 5  # Intervalo de tiempo para hacer pooling de dispositivos (en segundos)
ALLOWED_DEVICE_TYPES = set(['keyboard', 'mouse'])  # Tipos de dispositivos a configurar
SETUP_FUNCTION_MAP = {
    'keyboard': setup_keyboard,
    # 'mouse': setup_mouse,  # Si se desea agregar soporte para mouse, se puede definir una función similar a setup_keyboard y agregarla aquí
}


#Variables comunes

setupDevices = set[str]()

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
            setupDevices.clear()  # Limpiar la lista de dispositivos configurados para forzar reconfiguración al reconectar
            cleaned = True
            break  # Salir del bucle después de limpiar, no es necesario seguir verificando
           
    
    if cleaned:
        print('Reiniciando openrazer daemon para refrescar la lista de dispositivos...')
        subprocess.run(['systemctl', '--user', 'restart', 'openrazer-daemon'], check=True)
        cleaned = False


def setupDevice(device: RazerDevice):
    if device._pid in setupDevices:
        #print(f"El dispositivo {device.name} con PID {device._pid} ya está configurado, omitiendo...")
        return
    print(f"Configurando {device.type} con nombre {device.name} y PID {device._pid}...")
    setup_function = SETUP_FUNCTION_MAP.get(device.type) or (lambda x: None)
    try:
        setup_function(device)
        setupDevices.add(int(device._pid))
    except Exception as e:
        print(f"Error al configurar el dispositivo {device.name} con PID {device._pid}: {e}")
        
        return
    


def main():
    while True:
        devices = pollDevices()
        # Eliminar dispositivos que ya no están conectados
        cleanupDevices(devices)
        for device in devices:
            setupDevice(device)
        time.sleep(POLLING_INTERVAL)
                    
                    
main()













