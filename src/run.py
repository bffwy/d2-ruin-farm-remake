import sys
import os
import time
import multiprocessing

multiprocessing.freeze_support()

# try:
from TaskControl.RuinFarmTask import RuinFarmTask
from settings import base_settings, monitor_settings
from TaskControl.Base.CommonLogger import my_logger
from TaskControl.Base.TimerManager import TimerManager
from my_window.MainWindow import log_window
from utils import get_log_path, active_window


def main():
    my_logger.info(base_settings)
    my_logger.info(monitor_settings)
    my_logger.info("程序启动")

    active_window()
    new_task = RuinFarmTask()
    new_task.start()


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback

        traceback.print_exc()
        with open(get_log_path(), "a", encoding="utf-8") as f:
            f.write(traceback.format_exc() + "\n")
            f.write(f"{e}\n")

        active_window("Visual Studio Code")
        my_logger.critical(e)
        my_logger.info("程序已停止，请检查日志文件")
        # _ = input("按回车键退出...")
    finally:
        log_window.close_window()
        TimerManager.clear_timers()


# pipenv run pyinstaller --noconfirm --onedir --console --clean "D:/Work/remake/src/run.py"
# pipenv run pyinstaller --noconfirm --onedir --console --debug "all" --clean "D:/Work/remake/src/run.py"
# pipenv run pyinstaller .\run.spec --noconfir
