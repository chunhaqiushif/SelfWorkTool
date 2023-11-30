import time
import pandas as pd
import os
import shutil
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess


# csv 读取
def csv_load(load_path):
    data_frame = pd.read_csv(load_path, encoding='gb2312', index_col=0)
    return data_frame
        

# csv 保存
def csv_save(data_frame, save_path):
    data_frame.to_csv(save_path, encoding='gb2312', na_rep='')


# config.csv 特定格修改
def csv_edit(data_frame, row, col, value, save_path = "", isSaveNow = True):
    data_frame.iat[row - 1, col] = value
    if isSaveNow == True:
        csv_save(data_frame, save_path)


# 字符拆分
def text_split(text, separator):
    if pd.isnull(text):
        return []
    lst = str(text).split(separator)
    return lst


# 文件移动
def file_move(file_path, to_dir_path):
    if not os.path.exists(to_dir_path):
        return -1
    aim_file_path = os.path.join(to_dir_path, os.path.basename(file_path))
    if os.path.exists(aim_file_path):
        os.remove(aim_file_path)
    shutil.move(file_path, to_dir_path)


# 创建提示文本窗
def warningMsgBox(title, msg, wndAlpha = 1):
    msg_box = QMessageBox(QMessageBox.Warning, title, msg)
    msg_box.setWindowOpacity(wndAlpha)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(":/icon/icon_designSimpleTool.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    msg_box.setWindowIcon(icon)
    msg_box.setWindowFlags(
        QtCore.Qt.Dialog | 
        QtCore.Qt.WindowStaysOnTopHint | 
        QtCore.Qt.WindowCloseButtonHint
    )
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.button(QMessageBox.Ok).setText("确认")
    msg_box.exec_()


# 获得当前时间
def get_time_token():
    time_token = time.strftime('[%H:%M:%S]', time.localtime(time.time()))
    return time_token


# 使用线程启动文件或打开文件夹
class OpenByThread(QThread):
    threadSign = pyqtSignal(int)  # 定义信号

    def __init__(self, runPath):
        super().__init__()
        self.runPath = runPath

    def run(self):
        os.startfile('%s' % self.runPath)


# 使用cmd运行指令
class RunCmdByThread(QThread):
    def __init__(self, consoleText):
        super(RunCmdByThread, self).__init__()
        self.consoleText = consoleText

    def run(self):
        subprocess.Popen('%s' % self.consoleText, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)