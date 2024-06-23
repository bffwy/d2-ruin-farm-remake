import tomllib
import dataclasses
from pathlib import Path
from utils import get_real_path

config_path = get_real_path("settings.toml", "config")

SETTINGS_PATH = Path(config_path)


@dataclasses.dataclass
class BaseSettings:
    log_level: str
    debug: bool

    使用DIM功能: bool
    开启log窗口: bool
    连续失败次数: int


@dataclasses.dataclass
class Config:
    检测技能前切枪: str
    检测技能就绪: int
    开boss到射击前: str
    射击终结: str
    藏头行为: str
    开boss: str
    打开地图和难度选择: str
    开启下一轮: str
    重置进度: str
    自杀: str


settings = tomllib.loads(SETTINGS_PATH.read_text("utf-8"))
base_settings = BaseSettings(**settings.pop("base"))
monitor_settings = Config(**settings.pop(f"monitor"))
