from TaskControl.Base.CheckTaskBase import CheckTaskBase
from TaskControl.my_directx import *
from TaskControl.Base.TimerManager import TimerManager


class PlayerDieCheckTask(CheckTaskBase):

    die_check_similarity = 0.8
    check_interval = 0.5

    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.finish_check = False
        self.stop = False

    def start_check(self):
        self.stop_check()
        self.stop = False
        self.finish_check = False
        self.check_player_die()

    def stop_check(self):
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
            self.timer_id = None
        self.finish_check = True
        self.stop = True

    def check_player_die(self):
        if self.finish_check:
            return
        check_die_mask_ratio = get_similarity_result(ConfigKeys.CHECK_DIE)
        if check_die_mask_ratio >= self.die_check_similarity:
            self.finish_check = True
            self.event.trigger()
            return
        self.timer_id = TimerManager.add_timer(self.check_interval, self.check_player_die)

    def double_check(self):
        if self.stop:
            return

        check_die_mask_ratio = get_similarity_result(ConfigKeys.CHECK_DIE)
        if check_die_mask_ratio >= self.die_check_similarity:
            self.finish_check = True
            self.event.trigger()
