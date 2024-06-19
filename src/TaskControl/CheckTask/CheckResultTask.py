from TaskControl.Base.BaseTask import Task
from TaskControl.my_directx import *
from screenshot import check_boss_exit
from TaskControl.Base.TimerManager import TimerManager
from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.Base.CommonLogger import my_logger


class CheckBossExitTask(CheckTaskBase):
    # 检测 boss 再终结技之后又出现
    check_interval = 0.3
    check_conf = 0.6
    save_result = False

    def __init__(self):
        super().__init__()
        self.timer_id = None

    def start_check(self):
        self.check_boss_exit_timer()

    def stop_check(self):
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
            self.timer_id = None

    def check_boss_exit_timer(self):
        my_logger.info(f"check_boss_exit_timer")
        ret = check_boss_exit(self.check_conf, self.save_result)
        my_logger.info(f"check_boss_exit_timer ret={ret}")
        if ret:
            self.event.trigger()
            return
        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_boss_exit_timer)


class CheckCompleteTask(CheckTaskBase):

    check_interval = 0.3
    check_similarity = 0.1

    # 检测 boss 血条消失
    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.finish_check = False
        self.stop = False
        self.timeout_timer_id = None

    def start_check(self):
        self.stop_check()
        self.stop = False
        self.finish_check = False
        self.event.triggered = False
        self.check_boss_name_exist()
        self.timeout_timer_id = TimerManager.add_timer(30, self.event_time_out)

    def stop_check(self):
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
            self.timer_id = None
        self.stop = True
        self.finish_check = True

    def event_time_out(self):
        my_logger.info(f"CheckRebornTask time_out")
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
        self.event.data = {"boss_die": False, "hp_bar_ratio": 0}
        super().event_time_out()

    def check_boss_name_exist(self):
        if self.finish_check:
            return

        boss_name_mask_ratio = get_similarity_result(ConfigKeys.BOSS_NAME)
        my_logger.info(f"check_boss_name_exist: {boss_name_mask_ratio}")
        if boss_name_mask_ratio <= self.check_similarity:
            TimerManager.add_timer(1.5, self.delay_enter_map)

        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_boss_name_exist)

    def delay_enter_map(self):
        boss_name_mask_ratio = get_similarity_result(ConfigKeys.BOSS_NAME)
        if boss_name_mask_ratio <= self.check_similarity:
            my_logger.success("boss血条消失，本轮结算成功")
            self.event.data = {"boss_die": True, "hp_bar_ratio": boss_name_mask_ratio}
            self.event.trigger()
            if self.timer_id:
                TimerManager.cancel_timer(self.timer_id)


class CheckResultTask(Task):
    def __init__(self):
        super().__init__()
        self.boss_alive_check = CheckBossExitTask()
        self.boss_alive_check.register_event(self.on_boss_alive)

        self.boss_die_check = CheckCompleteTask()
        self.boss_die_check.register_event(self.on_boss_die)
        self.stop = True

    def start(self):
        my_logger.info(f"start:CheckResultTask")
        self.stop = False
        self.boss_alive_check.start()
        self.boss_die_check.start()

    def stop_check(self):
        self.boss_alive_check.stop_check()
        self.boss_die_check.stop_check()
        self.stop = True

    def on_boss_die(self, event):
        self.event.data = event.data
        self.trigger()

    def on_boss_alive(self, event):
        my_logger.info("boss血条重新刷新, 本轮结算失败")
        self.event.data = {"boss_die": False}
        self.trigger()

    def trigger(self):
        if self.stop:
            return

        self.boss_alive_check.stop_check()
        self.boss_die_check.stop_check()
        self.event.trigger()
