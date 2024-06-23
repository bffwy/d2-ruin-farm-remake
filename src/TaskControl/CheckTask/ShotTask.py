from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.my_directx import *
from TaskControl.Base.TimerManager import TimerManager
from PIL import ImageGrab
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

    def start_check(self):
        return
        if get_files_num() >= 400:
            return
        self.stop_check()
        self.finish_check = False
        random_start = random.uniform(0.2, 3)
        self.timer_id = TimerManager.add_timer(random_start, self.shot_all_screen)

    def shot_all_screen(self):
        if self.finish_check:
            return
        image = ImageGrab.grab(all_screens=True)
        uuid_str = uuid.uuid4()
        file_name = f"{uuid_str}_all.png"
        image.save(f"./debug/yolov8/{file_name}")
        random_start = random.uniform(1, 3)
        self.timer_id = TimerManager.add_timer(random_start, self.shot_all_screen)
