import asyncio
import threading
import json
import time
from D2API.api import move_items_from_postmaster_to_vault

from TaskControl.Base.BaseTask import Task, Event
from TaskControl.CheckTask.CheckResultTask import CheckResultTask
from TaskControl.CheckTask.CheckXReadyTask import CheckXReadyTask
from TaskControl.CheckTask.EnterMapTask import EnterMapTask
from TaskControl.CheckTask.PlayerDieCheckTask import PlayerDieCheckTask
from TaskControl.CheckTask.ShotTask import ShotTask
from TaskControl.CheckTask.CheckRebornTask import CheckRebornTask
from TaskControl.my_directx import (
    wake_up_boss,
    shot_and_do_finisher,
    refresh_checkpoint,
    hide_indebted_kindess,
    async_hide_indebted_kindess,
    WAKE_UP_SLEEP_TIME,
    suicide_before_kick,
    release_key_on_cancel,
)
from TaskControl.Base.TimerManager import TimerManager, Global_Queue
from TaskControl.Base.CommonLogger import my_logger

from settings import monitor_settings, base_settings
from screenshot import ConfigKeys, get_similarity_result, init_image
from utils import get_log_path
from my_window.MainWindow import log_window


CONTINUOUS_FAIL_COUNT_MAX = base_settings.连续失败次数

init_image()


class Data:
    def __init__(self):
        self.start_count = 0
        self.finisher_count = 0
        self.success_count = 0
        self.die_before_kick_boss = 0
        self.success_try_times = 0

    def __str__(self) -> str:
        out_data = {
            "start_count": self.start_count,
            "finisher_count": self.finisher_count,
            "die_before_kick_boss": self.die_before_kick_boss,
            # "success_try_times": self.success_try_times,
            "success_count": self.success_count,
        }

        # 使用json.dumps将字典转化为json字符串 ,并格式化输出
        json_str = json.dumps(out_data, indent=4, ensure_ascii=False)
        return json_str


class RuinFarmTask(Task):
    def __init__(self):
        super().__init__()
        self.init_tasks()
        self.need_refresh_checkpoint = False
        self.continuous_fail_count = 0
        self.main_task = None
        self.thread_running = False
        self.data = Data()

    def init_tasks(self):
        self.check_x_ready = self.init_task(CheckXReadyTask, self.on_x_ready)
        self.enter_map = self.init_task(EnterMapTask, self.on_enter_map)
        self.player_die_check = self.init_task(PlayerDieCheckTask, self.on_player_die)
        self.check_result = self.init_task(CheckResultTask, self.on_check_result)
        self.shot_task = self.init_task(ShotTask)
        self.check_reborn_task = self.init_task(CheckRebornTask, self.on_player_reborn)

    def init_task(self, task_class, event_handler=None):
        task = task_class()
        if event_handler:
            task.register_event(event_handler)
        return task

    def start(self):
        Global_Queue.put((self.start_new_round, None))
        try:
            asyncio.run(self.check_queue())
        except Exception as e:
            import traceback

            with open(get_log_path(), "a", encoding="utf-8") as f:
                f.write(traceback.format_exc() + "\n")
                f.write(f"{e}\n")
            raise Exception

    async def check_queue(self):
        while True:
            while not Global_Queue.empty():
                result = Global_Queue.get_nowait()
                func, event = result
                self.log(f"check_queue on_event={func.__name__}")
                func(event)
            await asyncio.sleep(1 / 30)

    async def main(self):
        try:
            self.data.start_count += 1
            self.log(f"start main")
            await self.wake_up_boss()
            self.log(f"wake_up_boss completed")
            await asyncio.sleep(monitor_settings.等待黄血刷新时间 - WAKE_UP_SLEEP_TIME - 0.2)
            await self.shot_and_do_finisher()
            self.log(f"shot_and_do_finisher completed")
            await asyncio.sleep(0.1)
            await self.check_shield()
            # self.move_and_waiting_result()
            await self.async_move_and_waiting_result()
        except asyncio.CancelledError:
            self.log(f"main was cancelled")
            release_key_on_cancel()

    async def wake_up_boss(self):
        self.log(f"wake_up_boss")
        wake_up_boss()
        self.player_die_check.start()

    async def shot_and_do_finisher(self):
        shot_and_do_finisher()

    async def check_shield(self):
        hp_bar_mask_ratio = get_similarity_result(ConfigKeys.FINISH_HP_BAR)
        self.log(f"check_shield hp_bar_mask_ratio={hp_bar_mask_ratio}")
        if hp_bar_mask_ratio >= 0.8:
            self.data.finisher_count += 1
            self.log(f"check_shield SUCC", emit=True)
            await asyncio.sleep(2)
        else:
            await asyncio.sleep(1)
            hp_bar_mask_ratio = get_similarity_result(ConfigKeys.FINISH_HP_BAR)
            if hp_bar_mask_ratio >= 0.8:
                self.data.finisher_count += 1
                self.log(f"check_shield SUCC", emit=True)
                await asyncio.sleep(1)
            else:
                self.data.die_before_kick_boss += 1
                self.log(f"check_shield Fail", emit=True)
                # 等死亡检查开启下一轮
                suicide_before_kick(move_back=False)
                await asyncio.sleep(2)
        self.log(f"check_shield completed")

    async def async_move_and_waiting_result(self):
        await async_hide_indebted_kindess()
        self.log(f"waiting_result_check")
        self.check_result.start()
        self.shot_task.start()

    def move_and_waiting_result(self):
        hide_indebted_kindess()
        self.log(f"waiting_result_check")
        self.check_result.start()
        self.shot_task.start()

    def on_x_ready(self, event: Event):
        self.thread_running = False
        data = event.data
        check_time_out = data["check_time_out"]
        self.log(f"on_x_ready  time_out={int(check_time_out)}", emit=True)
        if check_time_out:
            # x 检查连续失败 15 次，可能进牢里了，重新进图试一试
            self.continuous_fail_count = CONTINUOUS_FAIL_COUNT_MAX + 1
            Global_Queue.put((self.start_new_round, None))
        else:
            if self.main_task and not self.main_task.done():
                self.main_task.cancel()
            self.main_task = asyncio.create_task(self.main())
            self.log(f"count_data:\n {self.data}")

    def on_player_die(self, event: Event):
        self.log(f"player_die", emit=True)
        self.stop_all_checks()
        self.start_check_player_reborn()

    def on_check_result(self, event: Event):
        data = event.data
        boss_die = data["boss_die"]
        hp_bar_ratio = data.get("hp_bar_ratio", 0)
        self.log(f"round_result boss_die={int(boss_die)},,hp={hp_bar_ratio:.2f}", emit=True)
        if boss_die:
            self.data.success_count += 1
            self.data.success_try_times += self.continuous_fail_count
            self.need_refresh_checkpoint = True
            self.continuous_fail_count = 0
            self.start_enter_map(reward=True)
            # TimerManager.add_timer(1, self.delay_enter_map)
        else:
            suicide_before_kick()
            self.start_check_player_reborn()

    def delay_enter_map(self):
        # self.start_enter_map(reward=True)
        normal_hp_bar_mask_ratio = get_similarity_result(ConfigKeys.NORMAL_HP_BAR)
        self.log(f"delay_enter_map {normal_hp_bar_mask_ratio:.2f}", emit=True)
        if normal_hp_bar_mask_ratio >= 0.8:
            Global_Queue.put((self.start_enter_map, True))
        else:
            self.stop_all_checks()
            suicide_before_kick()
            self.start_check_player_reborn()

    def start_enter_map(self, reward=False):
        # 进图关闭其它检测
        self.log(f"start_enter_map reward={reward}", emit=True)
        self.stop_all_checks()
        self.enter_map.start(reward)

    def on_enter_map(self, event: Event):
        self.log(f"enter_map_finish refresh={int(self.need_refresh_checkpoint)}", emit=True)

        if base_settings.使用DIM功能:
            data = event.data
            self.log(f"on_map_load_finish move_items={data.get('reward')}")
            if data.get("reward"):
                move_items_from_postmaster_to_vault()

        if self.need_refresh_checkpoint:
            self.need_refresh_checkpoint = False
            refresh_checkpoint()
        # 重新进图也要自杀，因为开始进图也会传送到牢里，先自杀一下
        suicide_before_kick(move_back=False)
        time.sleep(4)
        self.log("自杀完成")
        self.start_check_player_reborn()
        # self.clear_timer_and_restart()

    def start_check_player_reborn(self):
        self.log(f"start_check_player_reborn", emit=True)
        self.continuous_fail_count += 1
        self.stop_all_checks()
        self.check_reborn_task.start()

    def on_player_reborn(self, event):
        self.log(f"player_reborn", emit=True)
        self.clear_timer_and_restart()

    def cancel_main(self):
        if self.main_task and not self.main_task.done():
            self.main_task.cancel()
            self.log(f"round end", emit=True)
            self.main_task = None

    def start_new_round(self, _):
        self.log(f"start_new_round round={self.data.start_count}", emit=True)
        if self.continuous_fail_count > CONTINUOUS_FAIL_COUNT_MAX:
            self.continuous_fail_count = 0
            self.log(f"enter_map_cause CONTINUOUS_FAIL", emit=True)
            self.start_enter_map()
            return

        if not self.thread_running:
            self.thread_running = True
            t = threading.Thread(target=self.check_x_ready.start)
            self.log(f"start_check_x_ready", emit=True)

            t.setDaemon(True)
            t.start()

    def stop_all_checks(self):
        self.player_die_check.stop_check()
        self.shot_task.stop_check()
        self.check_result.stop_check()
        self.check_x_ready.stop_check()
        # 清空消息队列
        self.cancel_main()
        Global_Queue.queue.clear()
        TimerManager.clear_timers()

    def clear_timer_and_restart(self):
        self.log(f"clear_timer_and_restart")
        self.stop_all_checks()
        self.thread_running = False
        Global_Queue.put((self.start_new_round, None))

    def log(self, msg, emit=False):
        my_logger.info(msg)
        if emit and base_settings.开启log窗口:
            log_window.emit_log(msg)
