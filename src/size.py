from loguru import logger
from PIL import ImageGrab
from itertools import chain

MONITOR_WIDTH, MONITOR_HEIGHT = ImageGrab.grab().size
logger.info(f"屏幕分辨率: {MONITOR_WIDTH}x{MONITOR_HEIGHT}")

# 计算缩放比例
RESIZE_RATIO_WIDTH = MONITOR_WIDTH / 2560
RESIZE_RATIO_HEIGHT = MONITOR_HEIGHT / 1440


def resize(x, y):
    return int(x * RESIZE_RATIO_WIDTH), int(y * RESIZE_RATIO_HEIGHT)


def get_resize(*points):
    return tuple(chain.from_iterable(resize(*point) for point in points))


def get_resize_bridge(x, y):
    return get_resize((x, y))


X_BBOX = get_resize((252, 1233), (334, 1318))

HP_BAR_BBOX_ALIVE = get_resize((990, 128), (1110, 150))

HP_BAR_BBOX_FINISH = get_resize((990, 128), (1110, 150))

BOSS_NAME_BBOX = get_resize((857, 1300), (1705, 1320))

CHECK_DIE_BBOX = get_resize((0, 60), (610, 240))

ENTER_MAP_BBOX = get_resize((260, 100), (535, 170))

REBORN_BBOX = get_resize((155, 340), (365, 385))

CLASS_SKILL_BBOX = get_resize((340, 1228), (422, 1306))
