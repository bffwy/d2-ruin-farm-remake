import json
import asyncio
import time
import threading
import pydirectinput
import os
import sys

parent_dir_name = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir_name)
sys.path.append(os.path.dirname(parent_dir_name))

from utils import get_real_path, Singleton
from TaskControl.Base.CommonLogger import my_logger
from settings import monitor_settings
from screenshot import replace_coordinates

pydirectinput.PAUSE = 0


class ConfigManager(Singleton):
    def __init__(self):
        self.configs = {}
        self.action_map = {}
        self.load_action_map()

    def load_action_map(self):
        base_path = os.path.join("config", "act")
        subfolders = ["map", "mod", "behavior"]
        for subfolder in subfolders:
            full_path = get_real_path(subfolder, base_path)
            for file in os.listdir(full_path):
                if file.endswith(".json"):
                    action_name = os.path.splitext(file)[0]
                    self.action_map[action_name] = os.path.join(full_path, file)

    def get_config(self, action_name):
        if action_name not in self.configs:
            file_path = self.action_map.get(action_name)
            if file_path is None:
                return None
            self.configs[action_name] = self.load_config(file_path)
        return self.configs[action_name]

    def load_config(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config


def execute_action(action):
    my_logger.debug(f"execute_action: {action}")
    if action["type"] == "key":
        pydirectinput.keyDown(action["name"])
        time.sleep(action["duration"])
        pydirectinput.keyUp(action["name"])

    elif action["type"] == "mouse_move":
        if action.get("relative"):
            pydirectinput.move(*action["relative"], relative=True)
        elif action.get("absolute"):
            pos = action["absolute"]
            if action.get("base_on_2560"):
                pos = replace_coordinates(pos)
            pydirectinput.moveTo(*pos)

    elif action["type"] == "wait":
        time.sleep(action["duration"])

    elif action["type"] == "click":
        pos = action["absolute"]
        if action.get("base_on_2560"):
            pos = replace_coordinates(pos)
        pydirectinput.click(*pos)

    elif action["type"] == "leftClick":
        pydirectinput.click(button="left")
    elif action["type"] == "rightClick":
        pydirectinput.click(button="right")

    elif action["type"] == "mouseDown":
        pydirectinput.mouseDown(button=action["key"])
    elif action["type"] == "mouseUp":
        pydirectinput.mouseUp(button=action["key"])

    elif action["type"] == "press":
        pydirectinput.press(action["key"])

    elif action["type"] == "action":
        map_act = getattr(monitor_settings, action["name"], None) or action["name"]
        do_actions(map_act)


def _actions(config):
    for action in config["actions"]:
        if action.get("blocking", False):
            execute_action(action)
        else:
            threading.Thread(target=execute_action, args=(action,)).start()


def do_actions(action_name):
    config = ConfigManager().get_config(action_name)
    if config is None:
        my_logger.info(f"actions NotFound: {action_name}")
        return
    _actions(config)
    my_logger.info(f"actions Done: {action_name}")


# from utils import active_window

# active_window()
# time.sleep(2)
# do_actions("refresh_checkpoint")

# async def execute_action(action):
#     print(action)
#     if action["type"] == "key":
#         pydirectinput.keyDown(action["name"])
#         await asyncio.sleep(action["duration"])
#         pydirectinput.keyUp(action["name"])

#     elif action["type"] == "mouse_move":
#         if action.get("relative"):
#             pydirectinput.move(*action["relative"], relative=True)
#         elif action.get("absolute"):
#             pydirectinput.moveTo(*action["absolute"])

#     elif action["type"] == "wait":
#         await asyncio.sleep(action["duration"])

#     elif action["type"] == "click":
#         pydirectinput.click(*action["absolute"])

#     elif action["type"] == "leftClick":
#         pydirectinput.click(button="left")
#     elif action["type"] == "rightClick":
#         pydirectinput.click(button="right")

#     elif action["type"] == "mouseDown":
#         pydirectinput.mouseDown(button=action["key"])
#     elif action["type"] == "mouseUp":
#         pydirectinput.mouseUp(button=action["key"])

#     elif action["type"] == "press":
#         pydirectinput.press(action["key"])

#     elif action["type"] == "action":
#         map_act = getattr(monitor_settings, action["name"], None) or action["name"]
#         # call_do_actions(map_act)
#         await do_actions(map_act)


# async def _actions(config):
#     for action in config["actions"]:
#         if action.get("blocking", False):
#             await execute_action(action)
#         else:
#             # asyncio.create_task(execute_action(action))
#             threading.Thread(target=execute_action, args=(action,)).start()


# async def do_actions(action_name):
#     config = ConfigManager().get_config(action_name)
#     if config is None:
#         my_logger.info(f"actions NotFound: {action_name}")

#         return
#     await _actions(config)
#     my_logger.info(f"actions Done: {action_name}")


# def call_do_actions(action_name):
#     try:
#         loop = asyncio.get_event_loop()
#         if loop.is_running():
#             loop.create_task(do_actions(action_name))
#         else:
#             asyncio.run(do_actions(action_name))
#     except RuntimeError:
#         asyncio.run(do_actions(action_name))
