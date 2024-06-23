from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.my_directx import *
from screenshot import get_similarity
from TaskControl.Base.TimerManager import TimerManager
from TaskControl.Base.CommonLogger import my_logger


class EnterMapTask(CheckTaskBase):
    enter_map_time = 20
    check_load_map_time_out_interval = 10
    check_similarity = 0.7
    check_interval = 1

    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.timeout_timer_id = None
        self.check_timer_id = None
        self.finish_check = False

    def start(self, reward=False):
        self.enter_map(reward)

    def enter_map(self, reward):
        self.event.data = {"reward": reward}
        my_logger.info(f"开始进图 reward={reward}")
        start_next_round()
        self.timer_id = TimerManager.add_timer(self.enter_map_time, self.check_load_map)

    def check_load_map(self):
        self.timeout_timer_id = TimerManager.add_timer(self.check_load_map_time_out_interval, self.event_time_out)
        self.real_check_load_map()

    def real_check_load_map(self):
        x = get_similarity(self.check_image, self.check_box, self.base_on_2560, self.debug)
        if x >= self.check_similarity:
            my_logger.info(f"real_check_load_map finish similarity={x}")
            self.trigger()
            return
        self.check_timer_id = TimerManager.add_timer(self.check_interval, self.real_check_load_map)
