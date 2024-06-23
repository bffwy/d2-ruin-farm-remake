from TaskControl.Base.BaseTask import Task
from TaskControl.Base.TimerManager import TimerManager
from TaskControl.Base.CommonLogger import my_logger


# 检测任务base


class CheckTaskBase(Task):
    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.finish_check = False
        self.timeout_timer_id = None

    def start(self):
        self.start_check()

    def start_check(self):
        raise NotImplementedError

    def stop_check(self):
        TimerManager.cancel_timer(self.timer_id)
        TimerManager.cancel_timer(self.timeout_timer_id)
        self.finish_check = True

    def trigger(self):
        self.stop_check()
        self.finish_check = True
        self.event.trigger()

    def event_time_out(self):
        if self.finish_check:
            return
        my_logger.info(f"{self.__class__.__name__}: time_out")
        self.trigger()
