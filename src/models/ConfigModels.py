# ConfigModels.py
from typing import TypeAlias, TypedDict

RGBColor: TypeAlias = list[int]

class CustomKeyConfig(TypedDict):
    color: RGBColor
    key: str


CustomKeyRow: TypeAlias = dict[str, CustomKeyConfig]
CustomKeys: TypeAlias = dict[str, CustomKeyRow]


class DeviceConfig(TypedDict):
    brightness: int
    default_color: RGBColor
    custom_keys: CustomKeys


class UserConfig(TypedDict, total=False):
    keyboard: DeviceConfig
    mouse: DeviceConfig