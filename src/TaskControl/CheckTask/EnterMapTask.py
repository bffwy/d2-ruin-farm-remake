from TaskControl.Base.BaseTask import Task
from TaskControl.my_directx import *
from TaskControl.Base.TimerManager import TimerManager
from TaskControl.Base.CommonLogger import my_logger


class EnterMapTask(Task):
    enter_map_time = 20
    check_load_map_time_out_interval = 10
    check_similarity = 0.7
    check_interval = 1

    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.timeout_timer_id = None
        self.check_timer_id = None
        self.finish_check = False
        self.register_event(self.on_map_load)

    def start(self, reward=False):
        self.event.data = {"reward": reward}
        my_logger.info(f"开始进图 reward={reward}")
        self.event.triggered = False
        start_next_round(reward=reward)
        self.enter_map()

    def enter_map(self):
        self.timer_id = TimerManager.add_timer(self.enter_map_time, self.check_load_map)

    def check_load_map(self):
        self.timeout_timer_id = TimerManager.add_timer(self.check_load_map_time_out_interval, self.event_time_out)
        self.real_check_load_map()

    def real_check_load_map(self):
        x = get_similarity_result(ConfigKeys.ENTER_MAP_BBOX)
        if x >= self.check_similarity:
            my_logger.info(f"real_check_load_map finish similarity={x}")
            self.event.trigger()
            return
        self.check_timer_id = TimerManager.add_timer(self.check_interval, self.real_check_load_map)

    def on_map_load(self, event):
        # data = event.data
        # my_logger.info(f"on_map_load_finish move_items={data.get('reward')}")
        # if data.get("reward"):
        #     move_items_from_postmaster_to_vault()
        if self.timeout_timer_id:
            TimerManager.cancel_timer(self.timeout_timer_id)

    def event_time_out(self):
        my_logger.info(f"event_map time_out")
        if self.timer_id:
            TimerManager.cancel_timer(self.timer_id)
        super().event_time_out()
        # self.event.trigger()
