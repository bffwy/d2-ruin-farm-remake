import time
import asyncio

import win32gui
import win32con

import pydirectinput
from pydirectinput import (
    keyDown,
    keyUp,
    leftClick,
    move,
    moveTo,
    mouseUp,
    mouseDown,
    RIGHT,
    press,
)
from loguru import logger

from size import get_resize, get_w_resize, get_resize_bridge
from settings import monitor_settings, base_settings
from screenshot import timer_log

from screenshot import ConfigKeys, get_similarity_result

pydirectinput.PAUSE = 0


def press_and_hold_key(key: str, seconds: float):
    logger.debug(f'press key "{key}" {seconds} seconds')

    keyDown(key)
    time.sleep(seconds)
    keyUp(key)


def move_to_and_left_click(x: int = None, y: int = None):
    logger.debug(f"move to ({x}, {y}) and left click")

    pydirectinput.moveTo(x, y)
    time.sleep(0.1)
    pydirectinput.leftClick()


def run(secons: float):
    keyDown("shiftleft")
    time.sleep(0.001)
    keyDown("w")
    time.sleep(secons)
    keyUp("shiftleft")
    keyUp("w")


def open_map_and_switch_difficulty():
    # 打开地图
    press("m")
    time.sleep(1.2)

    # 点击战争领主的废墟
    moveTo(get_w_resize(2360))
    time.sleep(0.3)
    leftClick()

    # 点开难度选择
    time.sleep(1.5)
    move_to_and_left_click(*get_resize_bridge(1960, 1110))

    # 选择大师难度
    time.sleep(1.5)
    move_to_and_left_click(*get_resize_bridge(455, 460))


def start_next_round(reward=False):
    open_map_and_switch_difficulty()
    # 点击开始
    if reward:
        time.sleep(base_settings.进图等待间隔)
    else:
        time.sleep(0.5)
    move_to_and_left_click(*get_resize_bridge(2180, 1210))


def refresh_checkpoint():

    def _refresh_checkpoint():
        open_map_and_switch_difficulty()
        # F进度
        moveTo(*get_resize_bridge(1805, 1115))
        time.sleep(0.5)
        # pydirectinput.moveTo(*get_resize_bridge(1805, 1115))
        # time.sleep(1)
        press_and_hold_key("f", 4)
        for _ in range(2):
            press("esc")
            time.sleep(0.5)

    reset_time = base_settings.重置进度次数 if base_settings.重置进度次数 > 0 else 1
    for _ in range(reset_time):
        _refresh_checkpoint()
        time.sleep(1)

    logger.info("已重置进度")

    press("2")
    time.sleep(1)
    # 开启boss
    move(*monitor_settings.开boss鼠标偏移, relative=True)
    time.sleep(0.5)
    leftClick()


def switch_2_gun():
    # 切枪
    press("2")
    time.sleep(1)


def suicide_before_kick(move_back=True):
    # 切枪
    if move_back:
        x, y = monitor_settings.回头看boss
        move(-x, y, relative=True)
        time.sleep(0.2)
    press("3")
    time.sleep(1)
    move(0, 600, relative=True)
    time.sleep(0.2)
    leftClick()


WAKE_UP_SLEEP_TIME = 0


@timer_log
def wake_up_boss():
    # 切枪
    press("2")
    time.sleep(1)
    # 开启boss
    move(*monitor_settings.开boss鼠标偏移, relative=True)
    time.sleep(0.5)
    leftClick()
    time.sleep(0.2)

    # 跳x隐身
    press("space")
    time.sleep(0.2)
    press(base_settings.跳隐身按键)
    time.sleep(1 + WAKE_UP_SLEEP_TIME)

    # 移动到预设的位置
    if monitor_settings.隐身后往右走时间 > 0:
        press_and_hold_key("d", monitor_settings.隐身后往右走时间)
    else:
        press_and_hold_key("a", monitor_settings.隐身后往左走时间)
    press_and_hold_key("w", monitor_settings.隐身后往前走时间)

    # 射击黄血小怪
    mouseDown(button=RIGHT)
    time.sleep(0.5)
    move(*monitor_settings.射击黄血鼠标偏移, relative=True)


@timer_log
def shot_and_do_finisher():
    logger.info("shot hive and do finisher")
    leftClick()
    mouseUp(button=RIGHT)

    move(-30, 0, relative=True)
    time.sleep(0.01)
    # run_and_kill()
    # 终结小怪
    keyDown(base_settings.终结技按键)
    run(1.5)
    keyUp(base_settings.终结技按键)


def run_and_kill():
    keyDown("shiftleft")
    time.sleep(0.001)
    keyDown("w")
    # 终结小怪
    run_time = 1.7
    while run_time > 0:
        run_time -= 0.05
        press(base_settings.终结技按键)
        time.sleep(0.05)

    keyUp("shiftleft")
    keyUp("w")


RELEASE_KEY = True


async def async_hide_indebted_kindess():
    global RELEASE_KEY
    move(*monitor_settings.躲藏第一段位移镜头偏移, relative=True)
    keyDown("w")
    keyDown("shiftleft")
    await asyncio.sleep(monitor_settings.躲藏第一段位移时间)
    move(*monitor_settings.躲藏第二段位移镜头偏移, relative=True)
    RELEASE_KEY = False
    await asyncio.sleep(monitor_settings.躲藏第二段位移时间)

    keyUp("shiftleft")
    keyUp("w")
    RELEASE_KEY = True
    await asyncio.sleep(0.5)

    press(base_settings.埋头表情按键)
    await asyncio.sleep(2)
    move(*monitor_settings.回头看boss, relative=True)
    move(1, 0, relative=True)
    await asyncio.sleep(0.5)


def release_key_on_cancel():
    keyUp("shiftleft")
    keyUp("w")


def hide_indebted_kindess():
    move(*monitor_settings.躲藏第一段位移镜头偏移, relative=True)
    keyDown("w")
    keyDown("shiftleft")
    time.sleep(monitor_settings.躲藏第一段位移时间)
    move(*monitor_settings.躲藏第二段位移镜头偏移, relative=True)
    time.sleep(monitor_settings.躲藏第二段位移时间)

    keyUp("shiftleft")
    keyUp("w")
    time.sleep(0.5)
    press(base_settings.埋头表情按键)
    time.sleep(2)
    move(*monitor_settings.回头看boss, relative=True)
    move(*[1, 0], relative=True)
    time.sleep(1)


def active_window(match_string="Destiny 2"):

    def enum_windows():
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                windows.append((hwnd, win32gui.GetWindowText(hwnd)))

        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows

    windows = enum_windows()

    for hwnd, title in windows:
        if match_string in title:
            win32gui.ShowWindow(hwnd, 5)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
            win32gui.BringWindowToTop(hwnd)
            break
