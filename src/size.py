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


def get_w_resize(x):
    return int(x * RESIZE_RATIO_WIDTH)


def get_resize_bridge(x, y):
    return get_resize((x, y))


X_START_POSITION = get_resize((252, 1233))
X_WIDTH, X_HEIGHT = get_resize((82, 85))


X_START_POSITION = get_resize((252, 1233))
X_WIDTH, X_HEIGHT = get_resize((82, 85))

X_BBOX = (
    *X_START_POSITION,
    X_START_POSITION[0] + X_WIDTH,
    X_START_POSITION[1] + X_HEIGHT,
)

HP_BAR_BBOX_ALIVE = get_resize((990, 128), (1110, 150))

HP_BAR_BBOX_FINISH = get_resize((990, 128), (1110, 150))

BOSS_NAME_BBOX = get_resize((857, 1300), (1705, 1320))

CHECK_DIE_BBOX = get_resize((0, 60), (610, 240))

ENTER_MAP_BBOX = get_resize((260, 100), (535, 170))

REBORN_BBOX = get_resize((155, 340), (365, 385))

FULL_SCREEN_BBOX = get_resize((0, 0), (MONITOR_WIDTH, MONITOR_HEIGHT))
