from TaskControl.Base.BaseTask import Task
from screenshot import get_similarity, check_boss_exit
from TaskControl.Base.TimerManager import TimerManager
from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.Base.CommonLogger import my_logger


class CheckBossExitTask(CheckTaskBase):
    # 检测 boss 再终结技之后又出现
    check_interval = 0.3
    check_conf = 0.6
    save_result = False
    check_time_out = 30

    def __init__(self):
        super().__init__()
        self.timer_id = None

    def start_check(self):
        self.stop_check()
        self.finish_check = False
        self.check_boss_exit_timer()
        self.timeout_timer_id = TimerManager.add_timer(self.check_time_out, self.event_time_out)

    def check_boss_exit_timer(self):
        if self.finish_check:
            return
        ret = check_boss_exit(self.check_conf, self.save_result)
        my_logger.info(f"check_boss_exit_timer ret={ret}")
        if ret:
            self.trigger()
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
        self.timeout_timer_id = None
        self.delay_check_list = []

    def start_check(self):
        self.finish_check = False
        self.timeout_timer_id = TimerManager.add_timer(self.check_time_out, self.event_time_out)
        self.delay_check_list = []
        self.check_boss_name_exist()

    def stop_check(self):
        for timer_id in self.delay_check_list:
            TimerManager.cancel_timer(timer_id)
        self.delay_check_list = []
        return super().stop_check()

    def event_time_out(self):
        self.event.data = {"boss_die": False, "hp_bar_ratio": 0}
        super().event_time_out()

    def check_boss_name_exist(self):
        if self.finish_check:
            return

        boss_name_mask_ratio = get_similarity(self.check_image, self.check_box, self.base_on_2560, self.debug)
        my_logger.info(f"check_boss_name_exist: {boss_name_mask_ratio}")
        if boss_name_mask_ratio <= self.check_similarity:
            time_id = TimerManager.add_timer(1.5, self.delay_enter_map)
            self.delay_check_list.append(time_id)

        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_boss_name_exist)

    def delay_enter_map(self):
        # 为什么这么实现？因为这1.5s内能触发玩家死亡判断，死亡判断会比这个函数先执行
        boss_name_mask_ratio = get_similarity(self.check_image, self.check_box, self.base_on_2560, self.debug)
        if boss_name_mask_ratio <= self.check_similarity:
            my_logger.success("boss血条消失，本轮结算成功")
            self.event.data = {"boss_die": True, "hp_bar_ratio": boss_name_mask_ratio}
            self.trigger()


class CheckResultTask(Task):
    def __init__(self):
        super().__init__()
        self.boss_alive_check = CheckBossExitTask()
        self.boss_alive_check.register_event(self.on_boss_alive)

        self.boss_die_check = CheckCompleteTask()
        self.boss_die_check.register_event(self.on_boss_die)
        self.finish_check = False

    def start(self):
        my_logger.info(f"start:CheckResultTask")
        self.finish_check = False
        self.boss_alive_check.start()
        self.boss_die_check.start()

    def stop_check(self):
        self.boss_alive_check.stop_check()
        self.boss_die_check.stop_check()
        self.finish_check = True

    def on_boss_die(self, event):
        self.event.data = event.data
        self.trigger()

    def on_boss_alive(self, event):
        my_logger.info("boss血条重新刷新, 本轮结算失败")
        self.event.data = {"boss_die": False}
        self.trigger()

    def trigger(self):
        if self.finish_check:
            return
        self.finish_check = True
        self.boss_alive_check.stop_check()
        self.boss_die_check.stop_check()
        self.event.trigger()
