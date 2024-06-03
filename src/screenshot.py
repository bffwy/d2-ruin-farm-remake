import cv2
import numpy as np
from PIL import ImageGrab, Image
from utils import image_log, timer_log, result_log
from size import *
from functools import lru_cache
from yolov8Util import get_boss_result
import os


def convert_image_to_open_cv(image: Image.Image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


@lru_cache(maxsize=None)
def load_image_cv(image_path):
    try:
        return convert_image_to_open_cv(Image.open(image_path))
    except Exception as e:
        raise Exception(f"加载图片 {image_path} 失败") from e


def get_template_similarity(image: Image.Image, template: cv2.typing.MatLike):
    image_cv = convert_image_to_open_cv(image)
    result = cv2.matchTemplate(image_cv, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return min_val


def get_mask_ratio(image: np.ndarray, lower_bound: np.ndarray, upper_bound: np.ndarray):
    mask = cv2.inRange(image, lower_bound, upper_bound)
    return np.sum(mask == 255) / (image.size / 3)


class ConfigKeys:
    X = "x"
    BOSS_NAME = "boss_name"
    CHECK_DIE = "check_die"
    FINISH_HP_BAR = "finish_hp_bar"
    NORMAL_HP_BAR = "normal_hp_bar"
    ENTER_MAP_BBOX = "enter_map"
    REBORN_BBOX = "REBORN_TAG"


config = {
    ConfigKeys.X: {"path": "x", "bbox": X_BBOX},
    ConfigKeys.BOSS_NAME: {"path": "boss_name", "bbox": BOSS_NAME_BBOX},
    ConfigKeys.CHECK_DIE: {"path": "check_die_new", "bbox": CHECK_DIE_BBOX},
    ConfigKeys.FINISH_HP_BAR: {"path": "finisher_hp_bar", "bbox": HP_BAR_BBOX_FINISH},
    ConfigKeys.NORMAL_HP_BAR: {"path": "normal_hp", "bbox": HP_BAR_BBOX_ALIVE},
    ConfigKeys.ENTER_MAP_BBOX: {"path": "enter_map", "bbox": ENTER_MAP_BBOX},
    ConfigKeys.REBORN_BBOX: {"path": "reborn_tag_new", "bbox": REBORN_BBOX},
}


@image_log
@timer_log
def grab_image(bbox):
    return ImageGrab.grab(bbox=bbox)


def get_path_by_screen_size(path):
    MONITOR_WIDTH, MONITOR_HEIGHT = ImageGrab.grab().size
    return f"./asset/{path}_{MONITOR_WIDTH}.png"


def get_crop_path(path):
    return f"./asset/{path}.png"


@result_log
@timer_log
def get_similarity_result(key):
    global config
    local_config = config.get(key)
    if not local_config:
        raise Exception(f"无效的键：{key}")

    if "path" in local_config:
        real_path = get_path_by_screen_size(local_config["path"])
        if not os.path.exists(real_path):
            raise Exception(f"{real_path} 不存在, 影响到正常功能")

        image_cv = load_image_cv(real_path)
        grabbed_image = ImageGrab.grab(bbox=local_config["bbox"])
        return get_template_similarity(grabbed_image, image_cv)
    else:
        raise Exception("path 不存在")
        return get_mask_ratio(convert_image_to_open_cv(grab_image(local_config["bbox"])), *local_config["color_range"])


def check_boss_exit(conf=0.6, save=False):
    return get_boss_result(ImageGrab.grab(bbox=FULL_SCREEN_BBOX), conf, save=save)


def test_get_image(bbox):
    image = ImageGrab.grab(bbox)
    file_name = f"{test_get_image.__name__}.png"
    image.save(f"./debug/{file_name}")


def crop_image(image_path, path_name, bbox):
    image = Image.open(image_path)
    cropped_image = image.crop(bbox)
    save_path = get_path_by_screen_size(path_name)
    print(f"crop_image: {save_path} 保存成功")
    cropped_image.save(save_path)


def init_image():
    for key, math_config in config.items():
        path_name = math_config["path"]
        bbox = math_config["bbox"]
        real_path = get_path_by_screen_size(path_name)

        if not os.path.exists(real_path):
            crop_path = get_crop_path(path_name)
            if os.path.exists(crop_path):
                crop_image(crop_path, path_name, bbox)


# init_image()
# test_get_image(HP_BAR_BBOX_FINISH)
# print(get_similarity_result(ConfigKeys.CHECK_DIE))
