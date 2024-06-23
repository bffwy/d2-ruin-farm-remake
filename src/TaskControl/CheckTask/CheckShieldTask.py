from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.Base.TimerManager import TimerManager
from TaskControl.Base.CommonLogger import my_logger
from screenshot import get_similarity


class CheckShieldTask(CheckTaskBase):

    check_similarity = 0.8
    check_interval = 0.5
    check_time_out = 3

    def start_check(self):
        self.stop_check()
        self.finish_check = False
        self.timeout_timer_id = TimerManager.add_timer(self.check_time_out, self.event_time_out)
        self.check_shield()

    def check_shield(self):
        if self.finish_check:
            return
        mask_ratio = get_similarity(self.check_image, self.check_box, self.base_on_2560, self.debug)
        my_logger.info(f"check_shield: {mask_ratio}")
        if mask_ratio >= self.check_similarity:
            self.event.data = {"time_out": False}
            self.trigger()
            return
        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_shield)

    def event_time_out(self):
        self.event.data = {"time_out": True}
        super().event_time_out()
