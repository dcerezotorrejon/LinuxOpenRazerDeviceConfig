# Razer Keyboard Configurator

This project is a tool for personalizing the lighting and configuration of Razer keyboards on Linux using the `openrazer` library. It allows you to define custom colors for specific keys and adjust the overall brightness via a JSON configuration file.

## Features

- **Per-Key Configuration:** Define specific colors for each key using matrix coordinates.
- **Brightness Control:** Adjust the global brightness level of the device.
- **Automatic Detection:** The script constantly monitors for new compatible devices to apply configurations automatically.
- **JSON-Based:** Easy to edit and customize without touching the source code.

## How it Works (Project Logic)

The application follows a modular workflow to manage hardware settings:

1.  **Device Polling (`Script.py`):** The main script runs an infinite loop that checks for connected Razer devices. It uses a set of PIDs to keep track of which devices have already been configured, ensuring settings are only applied once per connection.
2.  **Dynamic Loading:** The configuration logic is decoupled from the main loop. `Script.py` dynamically imports `KeyboardSetup.py`, allowing the detection engine to stay clean and focused.
3.  **Matrix Mapping:** Razer keyboards are treated as a grid (rows and columns). The logic iterates through this matrix and performs a lookup in `KeyboardConfig.json`:
    *   If coordinates match a entry in the JSON, that specific RGB color is applied.
    *   Otherwise, it applies the defined `default_color`.
4.  **Hardware Sync:** Once the matrix is prepared in memory, a single `draw()` command is sent to the hardware, making the update instantaneous and flickering-free.

## Requirements

- **Operating System:** Linux.
- **Drivers:** [OpenRazer](https://openrazer.github.io/) installed and the daemon (`openrazer-daemon`) running.
- **Python:** Version 3.x.
- **Python Dependencies:** `openrazer-client`.

## Installation

1. Clone this repository or download the files.
2. Ensure `openrazer` is installed and your user belongs to the `plugdev` group.
3. Install the required Python library:
   ```bash
   pip install openrazer-client
   ```

## Configuration

The `KeyboardConfig.json` file controls the lighting behavior:

- `brightness`: Brightness level (0-100).
- `default_color`: Default color in RGB format `[R, G, B]`.
- `custom_keys`: A nested map (`Row -> Column -> Config`) defining colors for specific keys.

Example `KeyboardConfig.json`:
```json
{
    "brightness": 40,
    "default_color": [255, 255, 255],
    "custom_keys": {
        "0": {
            "0": {"color": [255, 0, 0], "key": "ESC"}
        }
    }
}
```

## Usage

To start the configurator:

```bash
python3 Script.py
```

## Project Structure

- `Script.py`: Main entry point that manages device polling and lifecycle.
- `KeyboardSetup.py`: Bridge logic that maps JSON data to the OpenRazer matrix.
- `KeyboardConfig.json`: User-defined settings for colors and brightness.
