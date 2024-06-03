from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.my_directx import *
from TaskControl.Base.TimerManager import TimerManager
from screenshot import FULL_SCREEN_BBOX, ImageGrab
import uuid
import random
import os


def get_files_num():
    path = "./debug/yolov8/"
    f = os.listdir(path)
    return len(f)


class ShotTask(CheckTaskBase):
    check_interval = 3

    # 截图的任务，用于yolov8的标签原图，正式没有用到
    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.finish_check = False
        self.stop = False

    def start_check(self):
        return
        if get_files_num() >= 400:
            return
        self.stop_check()
        self.stop = False
        self.finish_check = False
        random_start = random.uniform(0.2, 3)
        self.timer_id = TimerManager.add_timer(random_start, self.shot_all_screen)

    def stop_check(self):
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
            self.timer_id = None
        self.finish_check = True
        self.stop = True

    def shot_all_screen(self):
        if self.finish_check:
            return
        image = ImageGrab.grab(bbox=FULL_SCREEN_BBOX)
        uuid_str = uuid.uuid4()
        file_name = f"{uuid_str}_all.png"
        image.save(f"./debug/yolov8/{file_name}")
        random_start = random.uniform(1, 3)
        self.timer_id = TimerManager.add_timer(random_start, self.shot_all_screen)
