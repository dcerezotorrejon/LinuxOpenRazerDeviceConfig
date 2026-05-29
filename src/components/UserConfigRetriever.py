# UserConfigRetriever.py
import json
import os
from pathlib import Path
from typing import cast

from src.models.ConfigModels import UserConfig


CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "UserConfig.json"


_CONFIG_CACHE: UserConfig | None = None

def get_user_config(config_path: str | os.PathLike[str] = CONFIG_PATH, force_reload: bool = False) -> UserConfig | None:
    """Carga el archivo JSON de configuración."""
    global _CONFIG_CACHE
    if not force_reload and _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = Path(os.path.expanduser(str(config_path)))
    try:
        with config_path.open("r", encoding="utf-8") as archivo:
            config_data = json.load(archivo) or {}
            _CONFIG_CACHE = cast(UserConfig, config_data)
            return _CONFIG_CACHE
    except Exception as e:
        print(f"Error al cargar el archivo de configuración: {e}")
        return None