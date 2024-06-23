import asyncio
import threading
import json
import time
import traceback
from D2API.api import move_items_from_postmaster_to_vault

from TaskControl.Base.BaseTask import Task, Event
from TaskControl.CheckTask.CheckResultTask import CheckResultTask
from TaskControl.CheckTask.CheckXReadyTask import CheckXReadyTask, CheckDodgeReadyTask, CheckSwordReadyTask
from TaskControl.CheckTask.CheckShieldTask import CheckShieldTask
from TaskControl.CheckTask.EnterMapTask import EnterMapTask
from TaskControl.CheckTask.PlayerDieCheckTask import PlayerDieCheckTask
from TaskControl.CheckTask.ShotTask import ShotTask
from TaskControl.CheckTask.CheckRebornTask import CheckRebornTask
from TaskControl.my_directx import (
    real_wake_up_boss,
    wake_up_boss_and_move,
    shot_and_do_finisher,
    refresh_checkpoint,
    hide_indebted_kindess,
    async_hide_indebted_kindess,
    suicide_before_kick,
    release_key_on_cancel,
)
from TaskControl.Base.TimerManager import TimerManager, Global_Queue
from TaskControl.Base.CommonLogger import my_logger
from TaskControl.Base import GlobalVars
from screenshot import init_image

from settings import monitor_settings, base_settings
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
        self.shied_task_complete = False
        self.data = Data()

    def init_tasks(self):
        self.pre_check_task = self.init_task(self.get_pre_check_task(), self.on_pre_check)
        self.enter_map = self.init_task(EnterMapTask, self.on_enter_map)
        self.player_die_check = self.init_task(PlayerDieCheckTask, self.on_player_die)
        self.check_result = self.init_task(CheckResultTask, self.on_check_result)
        self.check_shield_task = self.init_task(CheckShieldTask, self.on_check_shield)
        self.shot_task = self.init_task(ShotTask)
        self.check_reborn_task = self.init_task(CheckRebornTask, self.on_player_reborn)

    def get_pre_check_task(self):
        if monitor_settings.检测技能就绪 == 1:
            return CheckXReadyTask
        elif monitor_settings.检测技能就绪 == 2:
            return CheckDodgeReadyTask
        elif monitor_settings.检测技能就绪 == 3:
            return CheckSwordReadyTask
        raise Exception("不支持的运行模式，请重新调整设置文件")

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
        loop = asyncio.get_event_loop()
        try:
            self.data.start_count += 1
            self.log(f"start main")
            await self.wake_up_boss_and_move()
            self.log(f"wake_up_boss_and_move completed")
            await self.shot_and_do_finisher()
            await self.wait_shied_result()
            await self.async_move_and_waiting_result()
        except asyncio.CancelledError:
            self.log(f"main was cancelled")
            release_key_on_cancel()

    async def wake_up_boss_and_move(self):
        self.log(f"wake_up_boss_and_move")
        wake_up_boss_and_move()
        self.player_die_check.start()

    async def shot_and_do_finisher(self):
        shot_and_do_finisher()
        self.shied_task_complete = False
        self.check_shield_task.start()

    async def wait_shied_result(self):
        wait_time = 10
        while not self.shied_task_complete and wait_time > 0:
            await asyncio.sleep(1)
            wait_time -= 1
        # 这个时候还没有完成终结动作，所以这里有个sleep
        await asyncio.sleep(1)

    def on_check_shield(self, event):
        data = event.data
        time_out = data["time_out"]
        self.shied_task_complete = True
        if time_out:
            self.log(f"check_shield Fail", emit=True)
            suicide_before_kick()
        else:
            self.data.finisher_count += 1
            self.log(f"check_shield Success", emit=True)
        self.log(f"check_shield completed")

    async def async_move_and_waiting_result(self):
        self.log(f"move_to_wait")
        hide_indebted_kindess()
        # await async_hide_indebted_kindess()
        self.log(f"waiting_result_check")
        self.check_result.start()
        # self.shot_task.start()

    def on_pre_check(self, event: Event):
        self.thread_running = False
        data = event.data
        check_time_out = data["check_time_out"]
        self.log(f"on_pre_check time_out={int(check_time_out)}", emit=True)
        self.log(f"class_skill={int(GlobalVars.class_skill_ready)}", emit=True)
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
        else:
            suicide_before_kick()

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
        real_wake_up_boss()
        time.sleep(1)
        suicide_before_kick()
        time.sleep(2)
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
            t = threading.Thread(target=self.pre_check_task.start)
            self.log(f"start_check_x_ready", emit=True)

            t.setDaemon(True)
            t.start()

    def stop_all_checks(self):
        self.player_die_check.stop_check()
        self.shot_task.stop_check()
        self.check_result.stop_check()
        self.pre_check_task.stop_check()
        self.check_shield_task.stop_check()
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
