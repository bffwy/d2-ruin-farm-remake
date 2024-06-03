import tomllib
from pathlib import Path
import dataclasses
import os
import configparser
from settings import base_settings
from utils import get_real_path


file_path = get_real_path("dim_settings.toml", "config")
SETTINGS_PATH = Path(file_path)


@dataclasses.dataclass
class Config:
    membership_type: str
    destiny_membership_id: str
    x_api_key: str
    client_id: str
    client_secret: str
    code: str
    refresh_token: str
    get_postmaster_class: tuple[str]
    armor_sum_required: int
    filter_items: tuple[int]


def get_default_config():
    return {
        "membership_type": "None",
        "destiny_membership_id": "",
        "x_api_key": "",
        "client_id": "",
        "client_secret": "",
        "code": "",
        "refresh_token": "",
        "get_postmaster_class": ("",),
        "armor_sum_required": 0,
        "filter_items": (0,),
    }


if base_settings.使用DIM功能:
    settings = tomllib.loads(SETTINGS_PATH.read_text("utf-8"))
    dim_settings = Config(**settings.pop("base"))
else:
    dim_settings = Config(**get_default_config())


def update_refresh_token(new_refresh_token):
    config = configparser.ConfigParser()
    config.read(file_path, encoding="utf-8")
    config["base"]["refresh_token"] = f'"{new_refresh_token}"'
    with open(file_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)
