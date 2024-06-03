from functools import wraps
from loguru import logger
import os
import sys


def image_log(func: callable):
    from datetime import datetime
    from settings import base_settings

    @wraps(func)
    def inner(*args, **kwargs):
        image = func(*args, **kwargs)
        if base_settings.debug:
            time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
            file_name = f"{func.__name__}_{time_str}.png"

            logger.debug(f"[{func.__name__}] 保存图片: {file_name}")
            image.save(f"./debug/{file_name}")
        return image

    return inner


def timer_log(func: callable):
    @wraps(func)
    def inner(*args, **kwargs):
        import time

        start_time = time.monotonic()
        result = func(*args, **kwargs)
        if args:
            logger.debug(f"[{func.__name__}]:{args[0]} 耗时: {time.monotonic() - start_time:.3f}s")
        else:
            logger.debug(f"[{func.__name__}]: 耗时: {time.monotonic() - start_time:.3f}s")
        return result

    return inner


def result_log(func: callable):
    from loguru import logger
    from functools import wraps

    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug(f"[{func.__name__}] 结果: {result:.3f}")
        return result

    return inner


def get_real_path(relative_path, dir_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, "..", dir_name)
    file_path = os.path.join(target_dir, relative_path)
    real_path = os.path.abspath(file_path)
    if not os.path.exists(real_path):
        with open(get_log_path(), "a", encoding="utf-8") as f:
            f.write(f"miss file : {real_path}" + "\n")
    return real_path


def get_log_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, "..", "logs")
    file_path = os.path.join(target_dir, "running.log")
    real_path = os.path.abspath(file_path)
    return real_path


# print(get_log_path())
# # 使用函数
# resource_path = get_real_path("yolov8/best.pt", "resource")
# print(resource_path)

# config_path = get_real_path("settings.toml", "config")
# print(config_path)


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance
