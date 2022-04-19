import os
import subprocess
import sys
import re
import csv

import pyperclip3
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog, QTableWidgetItem, QAbstractItemView
from ui_designSimpleTool import Ui_Dialog

global PathList, GMCode
# PathList = {}
GMCode = {}


# def initConfig():
#     configFile = open('config/setting.conf', 'r', encoding='utf-8', )
#     for line in configFile:
#         if line == "" or line == "\n":
#             continue
#         temp = line.split(":", 1)
#         PathList.update({temp[0]: temp[1].replace("\n", "")})
#     configFile.close()


def initGMCode():
    GMCodeFile = open('config/gmcode.txt', 'r', encoding='utf-8')
    for line in GMCodeFile:
        temp = line.split(":", 1)
        GMCode.update({temp[0]: temp[1].replace("\n", "")})
    GMCodeFile.close()


class HomePageWindow(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(HomePageWindow, self).__init__(parent)
        self.setupUi(self)  # 装载UI
        # initConfig()    # 初始化按钮配置
        initGMCode()    # 初始化GM搜索
        self.initUI()   # 初始化UI事件

    def initUI(self):

        self.btn_submitToSearch.clicked.connect(self.onSearchKeyClicked)
        self.le_consoleCodeSearch.textChanged.connect(self.onGMCodeSearch)
        self.btn_consoleCodeCopy.clicked.connect(self.onGMCodeCopy)
        self.cb_topThisWindow.toggled.connect(self.onTopThisWindowClicked)

        self.btn_pathSetting.clicked.connect(self.onPathSettingClick)
        self.btn_quickJumpReload.clicked.connect(self.onQuickJumpReloadClick)
        self.btn_quickJump.clicked.connect(self.onQuickJumpClick)

        self.tw_jumpListTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tw_jumpListTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.onQuickJumpReloadClick()

        self.btn_svnSubmit.clicked.connect(self.onCommitDataclicked)
        self.btn_svnUpdata.clicked.connect(self.onUpdataDataclicked)

    @pyqtSlot()
    # 根据选中行打开对应路径下的文件夹/文件
    def onQuickJumpClick(self):
        items = self.tw_jumpListTable.selectedItems()
        if len(items) != 0:
            self.onRunFileOrFolder(items[1].text())

    @pyqtSlot()
    # 刷新加载快速跳转列表
    def onQuickJumpReloadClick(self):
        JumpListFile = open('config/dirlist.csv', 'r')
        read = csv.reader(JumpListFile)
        read_row = len(list(read))
        JumpListFile.seek(0)
        self.tw_jumpListTable.setRowCount(read_row)
        self.tw_jumpListTable.setColumnCount(2)
        for index_r, valueList in enumerate(read):
            for index_c, value in enumerate(valueList):
                qtw_value = QTableWidgetItem(value)
                self.tw_jumpListTable.setItem(index_r, index_c, qtw_value)
                # 根据类型上色
                if index_c == 1:
                    if os.path.isfile(qtw_value.text()):
                        self.tw_jumpListTable.item(index_r, 0).setBackground(QBrush(QColor(221, 235, 247)))
                        self.tw_jumpListTable.item(index_r, 1).setBackground(QBrush(QColor(221, 235, 247)))
                    elif os.path.isdir(qtw_value.text()):
                        self.tw_jumpListTable.item(index_r, 0).setBackground(QBrush(QColor(255, 242, 204)))
                        self.tw_jumpListTable.item(index_r, 1).setBackground(QBrush(QColor(255, 242, 204)))
                    else:
                        self.tw_jumpListTable.item(index_r, 0).setForeground(QBrush(QColor(255, 0, 0)))
                        self.tw_jumpListTable.item(index_r, 1).setForeground(QBrush(QColor(255, 0, 0)))

    # 打开程序/目录
    def onRunFileOrFolder(self, runPath):
        if os.path.exists(runPath):
            # 创建新线程启动文件，避免卡住
            self.thread = OpenByThread(runPath)
            self.thread.start()
        else:
            msg_box = QMessageBox(QMessageBox.Warning, "错误提示", "找不到路径下的文件/文件夹")
            msg_box.setWindowFlags(QtCore.Qt.Dialog|QtCore.Qt.WindowStaysOnTopHint)
            msg_box.exec_()

    @pyqtSlot()
    # 启动批处理文件（用于新开cmd窗口启动服务器）
    def onRunBat(self, key):
        runPath = self.pathCheckAndReturn(key, 3)
        subprocess.Popen('%s' % runPath, creationflags=subprocess.CREATE_NEW_CONSOLE)

    @pyqtSlot()
    # 搜索GM指令
    def onGMCodeSearch(self):
        inputText = self.le_consoleCodeSearch.text()
        if inputText == "":
            self.le_consoleCodeSearchResult.setText("")
            return
        suggestions = []
        pattern = '.*?'.join(inputText)  # 模糊匹配
        regex = re.compile(pattern)
        for item in GMCode.keys():
            match = regex.search(item)
            if match:
                suggestions.append((len(match.group()), match.start(), item, GMCode[item]))
        suggestions = sorted(suggestions)
        outputText = ""
        for tip in suggestions:
            outputText = outputText + "@" + tip[2] + "<@" + tip[3] + "> "
        if outputText == "":
            outputText = "无匹配结果"
        self.le_consoleCodeSearchResult.setText(outputText)

    @pyqtSlot()
    # 复制GM指令首个搜索结果
    def onGMCodeCopy(self):
        outputText = self.le_consoleCodeSearchResult.text()
        regex = "<(@[0-9]+)>"
        firstMatch = re.search(regex, outputText)
        if firstMatch is None:
            return
        pyperclip3.copy(firstMatch.group(1))

    @pyqtSlot()
    # 启动FileLocatoer并在表格文件夹[.xls]中搜索字段
    def onSearchKeyClicked(self):
        inputText = self.le_inputSearchTextEditor.text()
        items = self.tw_jumpListTable.selectedItems()
        if len(items) != 0 and os.path.isdir(items[1].text()):
            searchPath = items[1].text()
        else:
            msg_box = QMessageBox(QMessageBox.Warning, "错误提示", "未选中目录或选中的并非文件夹")
            msg_box.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
            msg_box.exec_()
            return
        if inputText == "":
            searchText = 'FileLocatorPro_x86.exe'
        else:
            searchText = 'FileLocatorPro_x86.exe -d "%s" -c "%s"' % (searchPath, inputText)
        self.thread = RunCmdByThread(searchText)
        self.thread.start()

    @pyqtSlot()
    # SVN更新当前选中目录
    def onUpdataDataclicked(self):
        items = self.tw_jumpListTable.selectedItems()
        if not len(items) == 0:
            runPath = items[1].text()
            if os.path.exists(runPath) and os.path.isdir(runPath):
                self.SVNUpdataOrCommit(runPath, 'update')
            else:
                msg_box = QMessageBox(QMessageBox.Warning, "提示", "找不到路径下的文件夹或不是目录，更新失败")
                msg_box.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
                msg_box.exec_()

    @pyqtSlot()
    # 提交SVN当前选中目录
    def onCommitDataclicked(self):
        items = self.tw_jumpListTable.selectedItems()
        if not len(items) == 0:
            runPath = items[1].text()
            if os.path.exists(runPath) and os.path.isdir(runPath):
                self.SVNUpdataOrCommit(runPath, 'commit')
            else:
                msg_box = QMessageBox(QMessageBox.Warning, "提示", "找不到路径下的文件夹或不是目录，提交失败")
                msg_box.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
                msg_box.exec_()

    # SVN更新与提交，根据参数二决定执行类型
    def SVNUpdataOrCommit(self, runPath, operateCommand):
        drive = runPath.split(":", 1)[0]  # 获取盘符
        consoleText_1stPart = '%s: & cd %s & setlocal enabledelayedexpansion' % (drive, runPath)  # 拼接指令
        consoleText_2ndPart = '& TortoiseProc.exe /command:%s /path:"." /closeonend:0' % operateCommand
        consoleText = consoleText_1stPart + consoleText_2ndPart
        self.thread = RunCmdByThread(consoleText)
        self.thread.start()

    # Git更新与提交，根据参数二决定执行类型
    def GitUpdataOrCommit(self, runPath, operateCommand):
        drive = runPath.split(":", 1)[0]  # 获取盘符
        consoleText_1stPart = '%s: & cd %s & setlocal enabledelayedexpansion' % (drive, runPath)  # 拼接指令
        consoleText_2ndPart = '& TortoiseGitProc.exe /command:%s /path:"."' % operateCommand
        consoleText = consoleText_1stPart + consoleText_2ndPart
        self.thread = RunCmdByThread(consoleText)
        self.thread.start()

    @pyqtSlot()
    # 设置置顶
    def onTopThisWindowClicked(self):
        if self.cb_topThisWindow.isChecked():
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 置顶
        else:
            self.setWindowFlags(QtCore.Qt.Widget)  # 取消置顶
        self.show()

    @pyqtSlot()
    # 设置路径(懒得写了就直接开记事本改算逑）
    def onPathSettingClick(self):
        self.thread = OpenByThread('.\config')
        self.thread.start()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建一个QApplication，也就是你要开发的软件app
    mainWindow = HomePageWindow()  # 创建一个QMainWindow，用来装载你需要的各种组件、控件

    # 设置窗口置顶|设置窗口样式为仅有关闭按钮
    mainWindow.setWindowFlags(
        QtCore.Qt.WindowStaysOnTopHint |
        QtCore.Qt.WindowCloseButtonHint
    )

    mainWindow.show()  # 执行QMainWindow的show()方法，显示这个QMainWindow
    sys.exit(app.exec_())  # 使用exit()或者点击关闭按钮退出QApp
