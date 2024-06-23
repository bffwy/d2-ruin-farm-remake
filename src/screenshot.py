import cv2
import os
import json

import numpy as np
from PIL import ImageGrab, Image
from utils import image_log, timer_log, result_log, get_real_path
from size import *
from datetime import datetime
from functools import lru_cache
from yolov8Util import get_boss_result


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


@image_log
@timer_log
def grab_image(bbox):
    return ImageGrab.grab(bbox=bbox)


def get_path_by_screen_size(path):
    MONITOR_WIDTH, MONITOR_HEIGHT = ImageGrab.grab().size
    return f"./asset/{path}_{MONITOR_WIDTH}.png"


def get_crop_path(path):
    return f"./asset/{path}.png"


def check_bbox(bbox):
    if len(bbox) != 4:
        return False
    for i, coordinate in enumerate(bbox):
        if not isinstance(coordinate, int):
            return False
        if coordinate < 0:
            return False
        if i % 2 == 0 and coordinate > MONITOR_WIDTH:
            return False
        elif i % 2 == 1 and coordinate > MONITOR_HEIGHT:
            return False
    return True


def replace_coordinates(bbox):
    return [
        int(bbox[i] * RESIZE_RATIO_WIDTH) if i % 2 == 0 else int(bbox[i] * RESIZE_RATIO_HEIGHT)
        for i in range(len(bbox))
    ]


def get_similarity(path, bbox, base_on_2560, debug):
    real_path = get_path_by_screen_size(path)
    if not os.path.exists(real_path):
        raise Exception(f"{real_path} 不存在, 影响到正常功能")
    image_cv = load_image_cv(real_path)
    if not check_bbox(bbox):
        raise Exception(f"{bbox}: bbox 不合法")
    if base_on_2560:
        bbox = replace_coordinates(bbox)
    grabbed_image = grab_image(bbox)
    ret = get_template_similarity(grabbed_image, image_cv)
    if debug:
        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        file_name = f"{path}_{time_str}_{ret:.3f} debug.png"
        logger.debug(f"Debug 保存图片: {file_name}")
        grabbed_image.save(f"./debug/{file_name}")

    return ret


def check_boss_exit(conf=0.6, save=False):
    return get_boss_result(ImageGrab.grab(all_screens=True), conf, save=save)


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
    file_path = get_real_path("task_config.json", "config")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        for key, task_config in config.items():
            if "check_image" in task_config and "check_box" in task_config:
                path_name = task_config["check_image"]
                bbox = task_config["check_box"]
                real_path = get_path_by_screen_size(path_name)
                if not os.path.exists(real_path):
                    crop_path = get_crop_path(path_name)
                    if os.path.exists(crop_path):
                        crop_image(crop_path, path_name, bbox)


# init_image()
# test_get_image(X_BBOX)
# print(get_similarity_result(ConfigKeys.CHECK_DIE))
