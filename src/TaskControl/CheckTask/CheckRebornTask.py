from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.my_directx import *
from TaskControl.Base.TimerManager import TimerManager
from TaskControl.Base.CommonLogger import my_logger


class CheckRebornTask(CheckTaskBase):

    check_similarity = 0.8
    check_interval = 0.5
    reborn_time_out = 15

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
        self.timeout_timer_id = TimerManager.add_timer(self.reborn_time_out, self.event_time_out)
        self.check_reborn_tag()

    def stop_check(self):
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
            self.timer_id = None
        self.finish_check = True
        self.stop = True

    def check_reborn_tag(self):
        if self.finish_check:
            return
        mask_ratio = get_similarity_result(ConfigKeys.REBORN_BBOX)
        if mask_ratio >= self.check_similarity:
            self.finish_check = True
            if self.timeout_timer_id:
                TimerManager.cancel_timer(self.timeout_timer_id)
            self.event.trigger()
            return
        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_reborn_tag)

    def event_time_out(self):
        my_logger.info(f"CheckRebornTask time_out")
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
        super().event_time_out()
