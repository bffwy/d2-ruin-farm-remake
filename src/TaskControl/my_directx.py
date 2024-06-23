import time
import asyncio
import pydirectinput
from pydirectinput import keyUp, mouseUp, RIGHT
from loguru import logger

from settings import monitor_settings
from screenshot import timer_log
from TaskControl.ActControl import do_actions

pydirectinput.PAUSE = 0


def open_map_and_switch_difficulty():
    do_actions(monitor_settings.打开地图和难度选择)


def start_next_round():
    do_actions(monitor_settings.开启下一轮)


def refresh_checkpoint():
    do_actions(monitor_settings.重置进度)
    logger.info("已重置进度")


def switch_2_gun():
    do_actions(monitor_settings.检测技能前切枪)


def suicide_before_kick():
    do_actions(monitor_settings.自杀)


WAKE_UP_SLEEP_TIME = 0


@timer_log
def real_wake_up_boss():
    do_actions(monitor_settings.开boss)


@timer_log
def wake_up_boss_and_move():
    do_actions(monitor_settings.开boss到射击前)


@timer_log
def shot_and_do_finisher():
    logger.info("shot hive and do finisher")
    do_actions(monitor_settings.射击终结)


def hide_indebted_kindess():
    do_actions(monitor_settings.藏头行为)


async def async_hide_indebted_kindess():
    await do_actions(monitor_settings.藏头行为)

    # move(*monitor_settings.躲藏第一段位移镜头偏移, relative=True)
    # keyDown("w")
    # keyDown("shiftleft")
    # await asyncio.sleep(monitor_settings.躲藏第一段位移时间)
    # move(*monitor_settings.躲藏第二段位移镜头偏移, relative=True)
    # await asyncio.sleep(monitor_settings.躲藏第二段位移时间)
    # keyUp("shiftleft")
    # keyUp("w")
    # await asyncio.sleep(0.5)
    # press(base_settings.埋头表情按键)
    # await asyncio.sleep(2)
    # move(*monitor_settings.回头看boss, relative=True)
    # move(1, 0, relative=True)
    # await asyncio.sleep(0.5)


def release_key_on_cancel():
    keyUp("shiftleft")
    keyUp("w")
    mouseUp(button=RIGHT)
