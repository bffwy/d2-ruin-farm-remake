import sys
from TaskControl.Base.CommonLogger import my_logger
from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.my_directx import *
from TaskControl.Base.TimerManager import TimerManager


class CheckXReadyTask(CheckTaskBase):

    check_interval = 3
    check_similarity = 0.85
    re_enter_map_check_time = 20
    repeated_fail_max = 80

    def __init__(self):
        super().__init__()
        self.check_x_time = 0
        self.timer_id = None

    def start_check(self):
        self.stop_check()
        self.check_x_skill()

    def stop_check(self):
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
            self.timer_id = None

    def switch_2_gun(self):
        # 切枪
        press("2")
        time.sleep(1)

    def check_x_skill(self):
        self.switch_2_gun()
        self.check_x_time += 1
        x_similarity = get_similarity_result(ConfigKeys.X)
        my_logger.info(f"check_x_skill x_similarity:{x_similarity}")
        if x_similarity > self.check_similarity:
            my_logger.info("检测到X技能准备就绪")
            self.check_x_time = 0
            self.event.data = {"check_time_out": False}
            self.event.trigger()
            return

        if self.check_x_time >= self.repeated_fail_max:
            my_logger.info("连续失败太多次了， 结束进程")
            sys.exit(0)

        if self.check_x_time >= self.re_enter_map_check_time:
            my_logger.info(f"检测到X技能连续失败次数超过{self.re_enter_map_check_time}次，重新进本")
            self.event.data = {"check_time_out": True}
            self.event.trigger()
            self.check_x_time = 0
            return

        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_x_skill)
