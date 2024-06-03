import json
import os
from TaskControl.Base.TimerManager import Global_Queue
from utils import get_real_path


class Event:
    def __init__(self):
        self.data = {}
        self.triggered = False
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def trigger(self):
        for listener in self.listeners:
            if callable(listener):
                Global_Queue.put((listener, self))
                # listener(self)
        self.triggered = True


class Task:
    def __init__(self):
        self.event = Event()
        self.init()

    def init(self):
        file_path = get_real_path("task_config.json", "config")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            task_config = config.get(self.__class__.__name__)
            if task_config:
                for key, value in task_config.items():
                    setattr(self, key, value)

    def start(self):
        raise NotImplementedError

    def register_event(self, func):
        self.event.add_listener(func)

    def event_time_out(self):
        if self.event.triggered:
            return
        # self.event.data["time_out"] = 1
        self.event.trigger()
