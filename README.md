# Razer Device Configurator (Linux)

Tool for customizing Razer device lighting on Linux using OpenRazer.
It currently supports both keyboard and mouse configuration through JSON.

## Features

- Automatic detection of compatible devices (`keyboard` and `mouse`).
- Brightness configuration per device type.
- Matrix-based mapping for keyboards using `custom_keys` (`row -> column -> color`).
- Static color fallback for devices without exposed LED matrix support.
- System signal handling (SIGINT/SIGTERM) and resume handling through DBus.

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

1. `src/Script.py` periodically polls OpenRazer devices.
2. It tracks already configured devices to avoid reapplying settings every cycle.
3. `src/components/SetupDevice.py` (`SetupDeviceManager`) applies brightness and effects.
4. `src/components/Effects.py` applies matrix effects when available, or static fallback otherwise.
5. On disconnect/resume events, it cleans up state and may restart `openrazer-daemon`.

## Current Structure

- `src/Script.py`: main loop, detection, signals, and DBus handling.
- `src/components/DeviceRegistry.py`: registry of configured devices.
- `src/components/SetupDevice.py`: per-device setup manager.
- `src/components/Effects.py`: lighting logic (matrix/static).
- `src/components/UserConfigRetriever.py`: loads `config/UserConfig.json`.
- `src/models/ConfigModels.py`: typed config models.
- `config/UserConfig.json`: user configuration.

## Known Limitations

- Some mouse models expose LED zones differently depending on firmware/driver.
- Matrix support relies on advanced OpenRazer properties that may vary across versions.
- If you edit `UserConfig.json` while the script is running, you may need to restart the script to fully reapply changes.
