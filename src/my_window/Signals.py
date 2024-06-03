from PyQt5 import QtCore

from PyQt5.QtCore import QObject

from PyQt5.QtGui import QFont


class MySignals(QObject):
    # 定义一种信号，两个参数 类型分别是： 整数 和 字符串
    # 调用 emit方法 发信号时，传入参数 必须是这里指定的 参数类型
    text_print = QtCore.pyqtSignal(int, str)
    # 还可以定义其他种类的信号
    my_Signal = QtCore.pyqtSignal(str)
    new_comment = QtCore.pyqtSignal(bool, str)
    otherChange = QtCore.pyqtSignal(str, str)
    sizeChange = QtCore.pyqtSignal(str, int)
    fontChange = QtCore.pyqtSignal(QFont)


# 实例化
global_ms = MySignals()
