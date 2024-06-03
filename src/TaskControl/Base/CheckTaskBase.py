from TaskControl.Base.BaseTask import Task


# 检测任务base


class CheckTaskBase(Task):
    def __init__(self):
        super().__init__()

    def start(self):
        self.start_check()

    def start_check(self):
        raise NotImplementedError

    def stop_check(self):
        raise NotImplementedError
