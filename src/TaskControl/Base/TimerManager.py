import threading
import uuid
from queue import Queue
from TaskControl.Base.CommonLogger import my_logger
from utils import get_log_path

Global_Queue = Queue()


class TimerManager:
    timers = {}
    # lock = threading.Lock()
    lock = threading.RLock()  # Use RLock instead of Lock

    @classmethod
    def add_timer(cls, interval, func, args=(), repeat=False):
        timer_id = str(uuid.uuid4())
        timer = {"func": func, "args": args, "repeat": repeat, "interval": interval, "timer": None}
        with cls.lock:
            cls.timers[timer_id] = timer
        cls._start_timer(timer_id)
        return timer_id

    @classmethod
    def _start_timer(cls, timer_id):
        with cls.lock:
            timer = cls.timers[timer_id]
            timer["timer"] = threading.Timer(timer["interval"], cls._timer_callback, args=[timer_id])
            timer["timer"].daemon = True
            timer["timer"].start()

    @classmethod
    def _timer_callback(cls, timer_id):
        repeat = False
        with cls.lock:
            timer = cls.timers[timer_id]
            try:
                timer["func"](*timer["args"])
            except Exception as e:
                import traceback

                traceback.print_exc()
                with open(get_log_path(), "a", encoding="utf-8") as f:
                    f.write(traceback.format_exc() + "\n")
                    f.write(f"{e}\n")
            repeat = timer["repeat"]
            if not repeat:
                del cls.timers[timer_id]
        if repeat:
            cls._start_timer(timer_id)

    @classmethod
    def cancel_timer(cls, timer_id):
        with cls.lock:
            if timer_id in cls.timers:
                timer = cls.timers[timer_id]
                timer["timer"].cancel()
                del cls.timers[timer_id]

    @classmethod
    def clear_timers(cls):
        with cls.lock:
            for timer_id in list(cls.timers.keys()):  # Use list() to create a copy of keys to avoid RuntimeError
                cls.cancel_timer(timer_id)


# # Register clear_timers to be called on exit
# atexit.register(TimerManager.clear_timers)


# # 使用示例
# def my_func():
#     my_logger.info("Timer is up!")


# # 添加定时器
# timer_id = TimerManager.add_timer(5, my_func, repeat=True)
# my_logger.info(f"Timer ID: {timer_id}")

# 取消定时器
# TimerManager.cancel_timer(timer_id)
