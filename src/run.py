import sys
import os
import time
import multiprocessing

multiprocessing.freeze_support()

# try:
from TaskControl.RuinFarmTask import RuinFarmTask
from settings import base_settings, monitor_settings
from TaskControl.Base.CommonLogger import my_logger
from TaskControl.my_directx import active_window
from TaskControl.Base.TimerManager import TimerManager
from my_window.MainWindow import log_window
from utils import get_log_path


def main():

    import traceback

    # 打印main函数的调用栈
    stack = traceback.extract_stack()
    with open(get_log_path(), "a", encoding="utf-8") as f:
        for frame in stack:
            f.write(f'File "{frame.filename}", line {frame.lineno}, in {frame.name}\n')

    my_logger.info(base_settings)
    my_logger.info(monitor_settings)
    my_logger.info("程序启动")

    active_window()
    new_task = RuinFarmTask()
    time.sleep(3)
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
# pipenv run pyinstaller --noconfirm --onedir --console --debug "all" --clean --hidden-import=ultralytics "D:/Work/remake/src/run.py"
