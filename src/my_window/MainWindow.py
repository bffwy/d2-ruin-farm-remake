import sys
import os

# parent_dir_name = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(parent_dir_name)
# sys.path.append(os.path.dirname(parent_dir_name))

from my_window.LogDisplayWindow import *

from my_window.Signals import global_ms

# from Signals import global_ms

from PyQt5.QtCore import QCoreApplication

import datetime


class MainWindow:
    def __init__(self):
        # 主要对象
        self.app = QApplication(sys.argv)
        # self.app.setQuitOnLastWindowClosed(False)  # 最小化托盘用,关闭所有窗口也不结束程序
        self.display = DisplayWindow()  # 弹幕展示窗口
        # global_ms.my_Signal.connect(self.SignalHandle)

    def run(self):
        try:
            self.display.show()
            # sys.exit(self.app.exec_())
        except:
            logger.critical("**********************程序异常退出************************")

    def SignalHandle(self, value):
        print(value)

    def quitApp(self):
        # 关闭窗体程序
        QCoreApplication.instance().quit()
        sys.exit(0)

    def close(self):
        self.app.quit()


class MainWindowManager:
    def __init__(self):
        self.main_window = None

    def init(self):
        self.main_window = MainWindow()
        self.main_window.run()

    def emit_log(self, content):
        if not self.main_window:
            self.init()
        now = datetime.datetime.now()
        content = f"[{now.hour}:{now.minute}:{now.second}]: {content}"
        global_ms.new_comment.emit(True, f"{content}")

    def close_window(self):
        if self.main_window:
            self.main_window.close()
            self.main_window.quitApp()


log_window = MainWindowManager()


if __name__ == "__main__":
    main_window = MainWindow()
    main_window.run()
    global_ms.new_comment.emit(True, "[Notice]: LIVE Start!")
    global_ms.new_comment.emit(True, "[Notice]: LIVE Ended!")
    import time

    time.sleep(1)
    global_ms.new_comment.emit(True, "111: 1")
    time.sleep(2)
    global_ms.new_comment.emit(True, "222: 2")

    time.sleep(3)
    main_window.close()
    main_window.quitApp()
