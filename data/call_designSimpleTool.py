import os
import subprocess
import sys
import re

import pyperclip3
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from ui_designSimpleTool import Ui_Dialog

global PathList, GMCode
PathList = {}
GMCode = {}


def initConfig():
    configFile = open('setting.conf', 'r', encoding='utf-8', )
    for line in configFile:
        if line == "" or line == "\n":
            continue
        temp = line.split(":", 1)
        PathList.update({temp[0]: temp[1].replace("\n", "")})
    configFile.close()


def initGMCode():
    GMCodeFile = open('gmcode.txt', 'r', encoding='utf-8')
    for line in GMCodeFile:
        temp = line.split(":", 1)
        GMCode.update({temp[0]: temp[1].replace("\n", "")})
    GMCodeFile.close()


class HomePageWindow(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(HomePageWindow, self).__init__(parent)
        self.setupUi(self)
        initConfig()
        initGMCode()
        self.initUI()

    def initUI(self):
        self.btn_openUnityHub.clicked.connect(lambda: self.onRunFileOrFolder('UnityHub', 1))
        self.btn_openBeyondCompare.released.connect(lambda: self.onRunFileOrFolder('BeyondCompare', 1))
        self.btn_openDesignFolder.released.connect(lambda: self.onRunFileOrFolder('DesignFolder', 2))
        self.btn_openExcelTableFolder.released.connect(lambda: self.onRunFileOrFolder('DataXLSFolder', 2))
        self.btn_openExcelDataFolder.released.connect(lambda: self.onRunFileOrFolder('DataCSVFolder', 2))
        self.btn_openOnedriveFolder.released.connect(lambda: self.onRunFileOrFolder('OnedriveFolder', 2))
        self.btn_runSelfServer.released.connect(lambda: self.onRunBat('RunServerBat'))
        self.btn_openSelfServerFolder.released.connect(lambda: self.onRunFileOrFolder('ServerFolder', 2))
        self.btn_openProjectFolder.released.connect(lambda: self.onRunFileOrFolder('ProjectFolder', 2))
        self.btn_submitToSearch.clicked.connect(self.onSearchKeyClicked)
        self.le_consoleCodeSearch.textChanged.connect(self.onGMCodeSearch)
        self.btn_consoleCodeCopy.clicked.connect(self.onGMCodeCopy)
        self.cb_topThisWindow.toggled.connect(self.onTopThisWindowClicked)
        self.btn_updataData.clicked.connect(self.onUpdataDataclicked)
        self.btn_updataDesignFolder.clicked.connect(self.onUpdataDesignFolderclicked)
        self.btn_updataProjectFolder.clicked.connect(self.onUpdataProjectFolderclicked)
        self.btn_commitData.clicked.connect(self.onCommitDataclicked)
        self.btn_commitDesignFolder.clicked.connect(self.onCommitDesignFolderclicked)
        self.btn_commitProjectFolder.clicked.connect(self.onCommitProjectFolderclicked)
        self.btn_pathSetting.clicked.connect(self.onPathSettingClick)


    @pyqtSlot()
    # 打开程序
    def onRunFileOrFolder(self, key, rType):
        # 创建新线程启动文件，避免卡住
        runPath = ""

        # 若配置信息内缺少路径，则弹窗选择文件路径
        if key not in PathList.keys():
            runPath = self.relocation(rType)
            if runPath == "":                   # 用户取消操作，未获取到值的情形
                return
            PathList[key] = runPath
            self.writeToSetting()   # 写入配置文件
            initConfig()       # 重载配置
        else:
            runPath = PathList[key]
            # 若配置信息内的路径不存在，则删除该条目，并弹窗选择文件路径
            if not os.path.exists(runPath):
                runPath = self.relocation(rType)
                if runPath == "":  # 用户取消操作，未获取到值的情形
                    return
                PathList[key] = runPath
                self.writeToSetting()   # 写入配置文件
                initConfig()       # 重载配置
        self.thread = OpenByThread(runPath)
        self.thread.start()

    # 路径验证后返回
    def pathCheckAndReturn(self, key, rType):
        # 若配置信息内缺少路径，则弹窗选择文件路径
        runPath = ""
        if key not in PathList.keys():
            runPath = self.relocation(rType)
            if runPath == "":                   # 用户取消操作，未获取到值的情形
                return
            PathList[key] = runPath
            self.writeToSetting()   # 写入配置文件
            initConfig()       # 重载配置
        else:
            runPath = PathList[key]
            # 若配置信息内的路径不存在，则删除该条目，并弹窗选择文件路径
            if not os.path.exists(runPath):
                runPath = self.relocation(rType)
                if runPath == "":  # 用户取消操作，未获取到值的情形
                    return
                PathList[key] = runPath
                self.writeToSetting()   # 写入配置文件
                initConfig()       # 重载配置
        return runPath

    # 文件/文件夹路径重定位
    def relocation(self, relocationType):       # 1->文件 2->文件夹
        if relocationType == 1:
            get_filePath = QFileDialog.getOpenFileName(self, "选择文件", "./", "可执行程序 (*.exe)")
            return get_filePath[0]
        elif relocationType == 2:
            get_folderPath = QFileDialog.getExistingDirectory(self, "选取文件夹", "./")
            return get_folderPath
        elif relocationType == 3:
            get_batPath = QFileDialog.getOpenFileName(self, "选择文件", "./", "批处理文件 (*.bat)")
            return get_batPath[0]
        return ""

    # 将路径信息写入setting.conf
    def writeToSetting(self):
        needToWriteText = ""
        for key in PathList:
            needToWriteText = needToWriteText + key + ":" + PathList[key] + "\n"
        configFile = open('setting.conf', 'w', encoding='utf-8')
        configFile.writelines(needToWriteText)

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
        key = 'DataXLSFolder'
        if inputText == "":
            searchText = 'FileLocatorPro_x86.exe'
        else:
            searchPath = self.pathCheckAndReturn(key, 2)
            searchText = 'FileLocatorPro_x86.exe -d "%s" -c "%s"' % (searchPath, inputText)
        self.thread = RunCmdByThread(searchText)
        self.thread.start()

    @pyqtSlot()
    # 更新SVN表格
    def onUpdataDataclicked(self):
        key_xls = 'DataXLSFolder'
        key_csv = 'DataCSVFolder'
        self.SVNUpdataOrCommit(key_xls, 'update')
        self.SVNUpdataOrCommit(key_csv, 'update')

    @pyqtSlot()
    # 提交SVN表格
    def onCommitDataclicked(self):
        key_xls = 'DataXLSFolder'
        key_csv = 'DataCSVFolder'
        self.SVNUpdataOrCommit(key_xls, 'commit')
        self.SVNUpdataOrCommit(key_csv, 'commit')

    @pyqtSlot()
    # 提交SVN策划文件夹
    def onUpdataDesignFolderclicked(self):
        key = 'DesignFolder'
        self.SVNUpdataOrCommit(key, 'update')

    @pyqtSlot()
    # 提交SVN策划文件夹
    def onCommitDesignFolderclicked(self):
        key = 'DesignFolder'
        self.SVNUpdataOrCommit(key, 'commit')

    # 更新SVN工程文件夹
    @pyqtSlot()
    def onUpdataProjectFolderclicked(self):
        key = 'ProjectFolder'
        self.SVNUpdataOrCommit(key, 'update')

    @pyqtSlot()
    # 提交SVN工程文件夹
    def onCommitProjectFolderclicked(self):
        key = 'ProjectFolder'
        self.SVNUpdataOrCommit(key, 'commit')

    # SVN更新与提交，根据参数二决定执行类型
    def SVNUpdataOrCommit(self, key, operateCommand):
        # 获得并检查路径正确性
        runPath = self.pathCheckAndReturn(key, 2)
        # 意外情况终止
        if runPath == "":
            return
        drive = runPath.split(":", 1)[0]  # 获取盘符
        consoleText_1stPart = '%s: & cd %s & setlocal enabledelayedexpansion' % (drive, runPath)  # 拼接指令
        consoleText_2ndPart = '& TortoiseProc.exe /command:%s /path:"." /closeonend:0' % operateCommand
        consoleText = consoleText_1stPart + consoleText_2ndPart
        self.thread = RunCmdByThread(consoleText)
        self.thread.start()

    # Git更新与提交，根据参数二决定执行类型
    def GitUpdataOrCommit(self, key, operateCommand):
        # 获得并检查路径正确性
        runPath = self.pathCheckAndReturn(key, 2)
        # 意外情况终止
        if runPath == "":
            return
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
        self.thread = RunCmdByThread("notepad.exe setting.conf")
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
