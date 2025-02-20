import time
import pandas as pd
import json
import os
import sys
import shutil
from PIL import Image
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QFileIconProvider
from PyQt5.QtCore import QThread, pyqtSignal, QFileInfo
from PyQt5.QtGui import QIcon 
import subprocess

# 工具类

# csv 读取
def csv_load(load_path):
    data_frame = pd.read_csv(load_path, encoding='gb18030', index_col=0)
    return data_frame
        

# csv 保存
def csv_save(data_frame, save_path):
    data_frame.to_csv(save_path, encoding='gb18030', na_rep='')


# config.csv 特定格修改
def csv_edit(data_frame, row, col, value, save_path = "", isSaveNow = True):
    data_frame.iat[row - 1, col] = value
    if isSaveNow == True:
        csv_save(data_frame, save_path)


# json 读取
def json_load(load_path):
    with open(load_path, 'r', encoding='gb18030') as file:
        data = json.load(file)
    return data


# json 保存
def json_save(data, json_path):
    with open(json_path, 'w', encoding='gb18030') as file:
        json.dump(data, file,ensure_ascii=False, indent=2)


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


# 文件复制
def file_copy(file_path, to_dir_path):
    if not os.path.exists(to_dir_path):
        return -1
    aim_file_path = os.path.join(to_dir_path, os.path.basename(file_path))
    if os.path.exists(aim_file_path):
        os.remove(aim_file_path)
    shutil.copy2(file_path, to_dir_path)


# 创建提示文本窗
def warningMsgBox(title, msg, wndAlpha = 1):
    msg_box = QMessageBox(QMessageBox.Warning, title, msg, QMessageBox.Ok)
    msg_box.setWindowOpacity(wndAlpha)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(":/icon/icon_designSimpleTool.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    msg_box.setWindowIcon(icon)
    msg_box.setWindowFlags(
        QtCore.Qt.Dialog | 
        QtCore.Qt.WindowStaysOnTopHint | 
        QtCore.Qt.WindowCloseButtonHint
    )
    msg_box.button(QMessageBox.Ok).setText("确认")
    msg_box.exec_()


# 创建错误文本窗
def errorMsgBox(title, msg, wndAlpha = 1):
    msg_box = QMessageBox(QMessageBox.critical, title, msg, QMessageBox.Ok)
    msg_box.setWindowOpacity(wndAlpha)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(":/icon/icon_designSimpleTool.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    msg_box.setWindowIcon(icon)
    msg_box.setWindowFlags(
        QtCore.Qt.Dialog | 
        QtCore.Qt.WindowStaysOnTopHint | 
        QtCore.Qt.WindowCloseButtonHint
    )
    msg_box.button(QMessageBox.Ok).setText("确认")
    msg_box.exec_()



# 获得当前时间
def get_time_token():
    time_token = time.strftime('[%H:%M:%S]', time.localtime(time.time()))
    return time_token


# 获取文件icon
def get_file_icon(path):
    provider = QFileIconProvider()
    info = QFileInfo(path)
    icon = QIcon(provider.icon(info))
    return icon


# 颜色代码转RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')  # 去除可能的 '#' 前缀
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b


# 获取svn操作指令
def get_svn_command(path, command) -> str:
    all_command = ["update", "commit"]
    if os.path.exists(path) and os.path.isdir(path):
        if not command in all_command:
            return ""
        drive = path.split(":", 1)[0]  # 获取盘符
        consoleText_1stPart = '%s: & cd %s & setlocal enabledelayedexpansion' % (drive, path)  # 拼接指令
        consoleText_2ndPart = '& TortoiseProc.exe /command:%s /path:"." /closeonend:0' % command
        consoleText = consoleText_1stPart + consoleText_2ndPart
        return consoleText
    else:
        return ""


# 使用线程启动文件或打开文件夹
class OpenByThread(QThread):
    threadSign = pyqtSignal(int)  # 定义信号

    def __init__(self, runPath):
        super().__init__()
        self.runPath = runPath

    def run(self):
        os.startfile('%s' % self.runPath)
        self.threadSign.emit(1)


# 使用cmd运行指令
class RunCmdByThread(QThread):
    threadSign = pyqtSignal(int)  # 定义信号
    def __init__(self, consoleText):
        super(RunCmdByThread, self).__init__()
        self.consoleText = consoleText

    def run(self):
        subprocess.Popen('%s' % self.consoleText, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)


# 启动cmd运行多条连续指令
class RunCmdsByThread(QThread):
    threadSign = pyqtSignal(int)  # 定义信号
    newText = pyqtSignal(str)
    def __init__(self, consoleTexts_arr, cwd = ""):
        super(RunCmdsByThread, self).__init__()
        self.consoleTexts_arr = consoleTexts_arr
        self.cwd = cwd


    def run(self):
        for consoleText in self.consoleTexts_arr:
            if self.cwd != "":
                subprocess.run(
                    consoleText, cwd=self.cwd, shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
            else:
                subprocess.run(
                    consoleText, shell=True, 
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
        self.threadSign.emit(1)


# 运行bat指令
class RunBatsByThread(QThread):
    finished_signal = pyqtSignal()
    def __init__(self, bat_paths: list):
        super(RunBatsByThread, self).__init__()
        self.bat_paths = bat_paths


    def run(self):
        try:
            for path in self.bat_paths:
                subprocess.call(path, shell=True)
        except Exception as e:
            warningMsgBox("提示", e)
        self.finished_signal.emit()





# 检查目录、配置文件是否完整，存在缺失时补充模板文件(仅主程序，不包含addons内的模块)
def init_conf():
    pass


# 截取print输出重定向至QTextBrowser
class StdoutRedirector:
    def __init__(self, text_browser, addline = True):
        self.text_browser = text_browser
        self.addline = addline


    def write(self, message):
        if self.addline:
            self.text_browser.append(message)
        else:
            self.text_browser.insertPlainText(message)


    def flush(self):
        pass


    # def restore(self):
    #     sys.stdout = self._default_stdout  # 恢复默认的 stdout