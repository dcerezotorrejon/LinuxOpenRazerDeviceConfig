# UserConfigRetriever.py
import json
import os
from pathlib import Path
from typing import cast

from src.models.ConfigModels import UserConfig


CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "UserConfig.json"


class ConfigLoader:
    def __init__(self, config_path: str | os.PathLike[str] = CONFIG_PATH):
        self.config_path = Path(os.path.expanduser(str(config_path)))

    def load(self) -> UserConfig | None:
        """Carga el archivo JSON de configuración."""
        try:
            with self.config_path.open("r", encoding="utf-8") as archivo:
                config_data = json.load(archivo) or {}
                return cast(UserConfig, config_data)
        except Exception as e:
            print(f"Error al cargar el archivo de configuración: {e}")
            return None