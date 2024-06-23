import sys
import time
from TaskControl.Base.CommonLogger import my_logger
from TaskControl.Base.CheckTaskBase import CheckTaskBase
from screenshot import get_similarity
from TaskControl.Base.TimerManager import TimerManager
from TaskControl.Base import GlobalVars
from TaskControl.my_directx import switch_2_gun


class CheckXReadyTask(CheckTaskBase):

    check_interval = 3
    check_similarity = 0.85
    repeated_fail_max = 80

    def __init__(self):
        super().__init__()
        self.check_x_time = 0
        self.timer_id = None
        self.repeated_fail_time = 0

    def start_check(self):
        self.stop_check()
        GlobalVars.class_skill_ready = False
        self.check_x_skill()

    def check_x_skill(self):
        switch_2_gun()
        self.check_x_time += 1
        x_similarity = get_similarity(self.check_image, self.check_box, self.base_on_2560, self.debug)

        my_logger.info(f"check_x_skill x_similarity:{x_similarity}")
        if x_similarity > self.check_similarity:
            my_logger.info("检测到X技能准备就绪")
            self.check_x_time = 0
            GlobalVars.class_skill_ready = False
            self.event.data = {"check_time_out": False}
            self.repeated_fail_time = 0
            self.trigger()
            return

        if self.repeated_fail_time >= self.repeated_fail_max:
            my_logger.info("连续失败太多次了， 结束进程")
            sys.exit(0)

        if self.check_x_time >= self.re_enter_map_check_time:
            my_logger.info(f"检测到X技能连续失败次数超过{self.re_enter_map_check_time}次，重新进本")
            self.event.data = {"check_time_out": True}
            self.check_x_time = 0
            self.repeated_fail_time += self.re_enter_map_check_time
            self.trigger()
            return

        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_x_skill)


class CheckDodgeReadyTask(CheckTaskBase):
    check_interval = 3
    check_similarity = 0.85
    re_enter_map_check_time = 20
    repeated_fail_max = 80

    def __init__(self):
        super().__init__()
        self.check_time = 0
        self.timer_id = None
        self.repeated_fail_time = 0

    def start_check(self):
        self.stop_check()
        self.check_skill()

    def check_skill(self):
        self.check_time += 1
        class_skill_similarity = get_similarity(self.check_image, self.check_box, self.base_on_2560, self.debug)
        my_logger.info(f"check_skill similarity:{class_skill_similarity}")
        if class_skill_similarity > self.check_similarity:
            my_logger.info("检测到闪身技能准备就绪")
            GlobalVars.class_skill_ready = True
            self.event.data = {"check_time_out": False}
            self.repeated_fail_time = 0
            self.trigger()
            return

        if self.repeated_fail_time >= self.repeated_fail_max:
            my_logger.info("连续失败太多次了， 结束进程")
            sys.exit(0)

        if self.check_time >= self.re_enter_map_check_time:
            my_logger.info(f"检测到技能连续失败次数超过{self.re_enter_map_check_time}次，重新进本")
            self.event.data = {"check_time_out": True}
            self.check_time = 0
            self.repeated_fail_time += self.re_enter_map_check_time
            self.trigger()
            return

        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_skill)


class CheckSwordReadyTask(CheckTaskBase):

    check_interval = 3
    check_similarity = 0.85
    re_enter_map_check_time = 20
    repeated_fail_max = 80

    def __init__(self):
        super().__init__()
        self.check_time = 0
        self.timer_id = None
        self.repeated_fail_time = 0

    def start_check(self):
        self.stop_check()
        self.check_skill()

    def check_skill(self):
        self.check_time += 1

        my_logger.info("不用检测刀剑充能")
        self.event.data = {"check_time_out": False}
        self.event.trigger()
        GlobalVars.class_skill_ready = True
        self.repeated_fail_time = 0
