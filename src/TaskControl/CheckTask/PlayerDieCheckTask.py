from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.Base.TimerManager import TimerManager
from screenshot import get_similarity


class PlayerDieCheckTask(CheckTaskBase):

    die_check_similarity = 0.8
    check_interval = 0.5

    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.finish_check = False

    def start_check(self):
        self.stop_check()
        self.finish_check = False
        self.timeout_timer_id = TimerManager.add_timer(self.check_time_out, self.event_time_out)
        self.check_player_die()

    def check_player_die(self):
        if self.finish_check:
            return
        check_die_mask_ratio = get_similarity(self.check_image, self.check_box, self.base_on_2560, self.debug)
        if check_die_mask_ratio >= self.die_check_similarity:
            self.trigger()
            return
        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_player_die)
