# Razer Device Configurator (Linux)

Tool for customizing Razer device lighting on Linux using OpenRazer.
It currently supports both keyboard and mouse configuration through JSON.

## Features

- Automatic detection of compatible devices (`keyboard` and `mouse`).
- Brightness configuration per device type.
- Matrix-based mapping for keyboards using `custom_keys` (`row -> column -> color`).
- Static color fallback for devices without exposed LED matrix support.
- System signal handling (SIGINT/SIGTERM) and resume handling through DBus.
- Runtime architecture organized around classes and dedicated components.

## Requirements

- Linux.
- [OpenRazer](https://openrazer.github.io/) installed and `openrazer-daemon` running.
- Python 3.
- Python dependencies:

```bash
pip install openrazer-client dbus-python pygobject
```

Note: `dbus-python` and `pygobject` may also be installed from system packages depending on your distro.

## Run

From the project root:

```bash
python3 src/Script.py
```

## Configuration

The configuration file is `config/UserConfig.json`.

Per-device keys:

- `brightness`: brightness level (0-100).
- `default_color`: default RGB color `[R, G, B]`.
- `custom_keys`: matrix coordinate map (`row -> column -> {color, key}`).

Minimum example:

```json
{
    "keyboard": {
        "brightness": 60,
        "default_color": [255, 255, 255],
        "custom_keys": {
            "0": {
                "0": {"color": [255, 0, 0], "key": "ESC"}
            }
        }
    },
    "mouse": {
        "brightness": 100,
        "default_color": [255, 255, 255],
        "custom_keys": {}
    }
}
```

## Workflow

1. `src/Script.py` creates a `RazerScriptOrchestrator` instance and starts the runtime loop.
2. `src/components/DevicePoller.py` periodically polls OpenRazer devices and filters usable ones.
3. `src/components/DeviceRegistry.py` tracks already configured devices to avoid reapplying settings every cycle.
4. `src/components/SetupDevice.py` (`SetupDeviceManager`) applies brightness and delegates effects to `EffectsManager`.
5. `src/components/SystemEvents.py` handles OS signals and DBus resume events.
6. On disconnect/resume events, the orchestrator cleans up state and may restart `openrazer-daemon`.

## Current Structure

- `src/Script.py`: bootstrap and `RazerScriptOrchestrator` lifecycle.
- `src/components/DevicePoller.py`: OpenRazer polling and device usability checks.
- `src/components/DeviceRegistry.py`: registry of configured devices.
- `src/components/SetupDevice.py`: per-device setup manager.
- `src/components/Effects.py`: `EffectsManager` for matrix/static lighting logic.
- `src/components/SystemEvents.py`: signal registration and DBus sleep/resume listener.
- `src/components/UserConfigRetriever.py`: `ConfigLoader` for loading `config/UserConfig.json`.
- `src/models/ConfigModels.py`: typed config models.
- `config/UserConfig.json`: user configuration.

## Runtime Design

- `RazerScriptOrchestrator` owns the runtime state and coordinates polling, setup, cleanup, and shutdown.
- `DevicePoller` isolates OpenRazer device discovery from the main loop.
- `SetupDeviceManager` focuses on device configuration only.
- `EffectsManager` encapsulates LED matrix and static fallback behavior.
- `SystemSignalHandler` and `SystemSleepListener` isolate OS integration concerns.
- `ConfigLoader` centralizes configuration loading.

## Known Limitations

- Some mouse models expose LED zones differently depending on firmware/driver.
- Matrix support relies on advanced OpenRazer properties that may vary across versions.
- If you edit `UserConfig.json` while the script is running, you may need to restart the script to fully reapply changes.
- Device tracking still uses the device name as registry key, so USB/wireless transitions may need further hardening depending on the model.
