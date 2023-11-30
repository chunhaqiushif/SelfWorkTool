import os
import sys
import re
import csv
import threading

import pyperclip3
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot, QUrl
from PyQt5.QtGui import QBrush, QColor, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem, QAbstractItemView

from ui_designSimpleTool import Ui_MainWnd
from ui_res_compress import Ui_ResCompressWnd
import pictures_rc

from ResourceCompressToZip import *
import util

global GMCode
GMCode = {}

root_path = os.path.abspath('.')
config_path = root_path + "\\" + "config"
dirlist = config_path + "\\" + "dirlist.csv"
gmcode_txt_path = config_path + "\\" + "gmcode.txt"
zip_path = root_path + "\\" + "zip"
log_path = root_path + "\\" + "log"
zip_conf_path = config_path + "\\" + "compress_conf.csv"


def initGMCode():
    GMCodeFile = open(gmcode_txt_path, 'r', encoding='utf-8')
    for line in GMCodeFile:
        temp = line.split(":", 1)
        GMCode.update({temp[0]: temp[1].replace("\n", "")})
    GMCodeFile.close()


# 主窗口
class HomePageWindow(QMainWindow, Ui_MainWnd):
    def __init__(self, parent=None):
        super(HomePageWindow, self).__init__(parent)
        self.setupUi(self)  # 装载UI
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
        )
        initGMCode()    # 初始化GM搜索
        self.initUI()   # 初始化UI事件

        global setting_btn_state
        setting_btn_state = -1


    def initUI(self):
        self.btn_submitToSearch.clicked.connect(self.onSearchKeyClicked)
        self.le_consoleCodeSearch.textChanged.connect(self.onGMCodeSearch)
        self.btn_consoleCodeCopy.clicked.connect(self.onGMCodeCopy)
        # self.cb_topThisWindow.toggled.connect(self.onTopThisWindowClicked)

        self.btn_pathSetting.clicked.connect(self.onPathSettingClick)
        self.btn_quickJumpReload.clicked.connect(self.onQuickJumpReloadClick)
        self.btn_quickJump.clicked.connect(self.onQuickJumpClick)

        self.tw_jumpListTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tw_jumpListTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.onQuickJumpReloadClick()

        self.btn_svnSubmit.clicked.connect(self.onCommitDataclicked)
        self.btn_svnUpdata.clicked.connect(self.onUpdataDataclicked)

        self.btn_setting.clicked.connect(self.onOpenSettingWndClicked)
        self.btn_resCompress.clicked.connect(self.onOpenResCompressWndClicked)

        self.cb_topThisWindow.toggled.connect(self.onTopThisWindowClicked)
        self.cb_translucentThisWindow.toggled.connect(self.onTranslucentThisWndClicked)
        self.btn_pathConfig.clicked.connect(self.onPathConfigOpenClicked)
        self.btn_consoleCode.clicked.connect(self.onGMCodeFileOpenClicked)

        # self.tw_jumpListTable.cellEntered.connect(self.onItemEntered)

        self.lb_coderSign.linkActivated.connect(self.open_gitHub_link)


    # 表格鼠标悬停时显示提示(存在问题，暂屏蔽)
    def onItemEntered(self, row, col):
        pass
        # item = self.tw_jumpListTable.item(row, col)
        # if item:
        #     self.setToolTip(item.text())
    
    
    @pyqtSlot()
    # 根据选中行打开对应路径下的文件夹/文件
    def onQuickJumpClick(self):
        items = self.tw_jumpListTable.selectedItems()
        if len(items) != 0:
            self.onRunFileOrFolder(items[1].text())


    @pyqtSlot()
    # 刷新.加载快速跳转列表和GM指令
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
                        self.tw_jumpListTable.item(index_r, 0).setBackground(QBrush(QColor(221, 235, 247, 200)))
                        self.tw_jumpListTable.item(index_r, 1).setBackground(QBrush(QColor(221, 235, 247, 200)))
                    elif os.path.isdir(qtw_value.text()):
                        self.tw_jumpListTable.item(index_r, 0).setBackground(QBrush(QColor(255, 242, 204, 200)))
                        self.tw_jumpListTable.item(index_r, 1).setBackground(QBrush(QColor(255, 242, 204, 200)))
                    else:
                        self.tw_jumpListTable.item(index_r, 0).setForeground(QBrush(QColor(255, 0, 0, 250)))
                        self.tw_jumpListTable.item(index_r, 1).setForeground(QBrush(QColor(255, 0, 0, 250)))
        self.tw_jumpListTable.resizeColumnToContents(0)

        initGMCode()


    # 打开程序/目录
    def onRunFileOrFolder(self, runPath):
        if os.path.exists(runPath):
            # 创建新线程启动文件，避免卡住
            self.thread = util.OpenByThread(runPath)
            self.thread.start()
        else:
            util.warningMsgBox("提示", "找不到路径下的文件/文件夹")


    @pyqtSlot()
    # 启动批处理文件（用于新开cmd窗口启动服务器）
    def onRunBat(self, key):
        runPath = self.pathCheckAndReturn(key, 3)
        util.RunCmdByThread(runPath)


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
            outputText = outputText + tip[2] + ":" + "<@" + tip[3] + "> "
        if outputText == "":
            outputText = "无匹配结果"
        self.le_consoleCodeSearchResult.setText(outputText)
        self.le_consoleCodeSearchResult.setCursorPosition(0)


    @pyqtSlot()
    # 复制GM指令首个搜索结果
    def onGMCodeCopy(self):
        outputText = self.le_consoleCodeSearchResult.text()
        regex = "<(@.*?)>"
        firstMatch = re.search(regex, outputText)
        copy_text = firstMatch.group(1)
        if firstMatch is None:
            return
        else:
            ls = firstMatch.group(1).split(" ")
            if len(ls) > 1:
                copy_text = ls[0]
        pyperclip3.copy(copy_text)


    @pyqtSlot()
    # 启动FileLocatoer并在选择的文件夹中搜索字段
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
        self.thread = util.RunCmdByThread(searchText)
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
                util.warningMsgBox("提示", "找不到路径下的文件夹或不是目录，更新失败")


    @pyqtSlot()
    # 提交SVN当前选中目录
    def onCommitDataclicked(self):
        items = self.tw_jumpListTable.selectedItems()
        if not len(items) == 0:
            runPath = items[1].text()
            if os.path.exists(runPath) and os.path.isdir(runPath):
                self.SVNUpdataOrCommit(runPath, 'commit')
            else:
                util.warningMsgBox("提示", "找不到路径下的文件夹或不是目录，提交失败")


    # SVN更新与提交，根据参数二决定执行类型
    def SVNUpdataOrCommit(self, runPath, operateCommand):
        drive = runPath.split(":", 1)[0]  # 获取盘符
        consoleText_1stPart = '%s: & cd %s & setlocal enabledelayedexpansion' % (drive, runPath)  # 拼接指令
        consoleText_2ndPart = '& TortoiseProc.exe /command:%s /path:"." /closeonend:0' % operateCommand
        consoleText = consoleText_1stPart + consoleText_2ndPart
        self.thread = util.RunCmdByThread(consoleText)
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
    # 打开工具集目录
    def onPathSettingClick(self):
        self.thread = util.OpenByThread(root_path)
        self.thread.start()


    @pyqtSlot()
    # 展开设置内容
    def onOpenSettingWndClicked(self):
        global setting_btn_state
        if setting_btn_state == -1:
            homeWnd.setMinimumHeight(905)
            homeWnd.setMaximumHeight(905)
            setting_btn_state = 1
            homeWnd.btn_setting.setText("设置 ▼")
        else:
            homeWnd.setMinimumHeight(820)
            homeWnd.setMaximumHeight(820)
            setting_btn_state = -1
            homeWnd.btn_setting.setText("设置 ▲")


    @pyqtSlot()
    # 打开资源压缩子窗口
    def onOpenResCompressWndClicked(self):
        resCompressWnd.setGeometry(
            int(self.geometry().center().x() - resCompressWnd.width() / 2),
            int(self.geometry().center().y() - resCompressWnd.height() / 2),
            resCompressWnd.width(),
            resCompressWnd.height()
        )
        resCompressWnd.show()


    @pyqtSlot()
    # 设置置顶\半透明
    def onTopThisWindowClicked(self):
        isRcpOpen = False
        if not resCompressWnd.isHidden():
            isRcpOpen = True
        if self.cb_topThisWindow.isChecked() and self.cb_translucentThisWindow.isChecked():
            homeWnd.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            resCompressWnd.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)
        else:
            homeWnd.setWindowFlags(QtCore.Qt.Widget)
            resCompressWnd.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.WindowCloseButtonHint)
        homeWnd.show()
        if isRcpOpen:
            resCompressWnd.show()


    @pyqtSlot()
    # 设置半透明
    def onTranslucentThisWndClicked(self):
        if self.cb_translucentThisWindow.isChecked():
            homeWnd.setWindowOpacity(0.75)
            resCompressWnd.setWindowOpacity(0.75)
        else:
            homeWnd.setWindowOpacity(1.0)
            resCompressWnd.setWindowOpacity(1.0)


    @pyqtSlot()
    # 路径配置表
    def onPathConfigOpenClicked(self):
        self.thread = util.OpenByThread(dirlist)
        self.thread.start()


    @pyqtSlot()
    # GM指令
    def onGMCodeFileOpenClicked(self):
        self.thread = util.OpenByThread(gmcode_txt_path)
        self.thread.start()


    # 打开Github链接
    def open_gitHub_link(self, url):
        QDesktopServices.openUrl(QUrl(url))


# 资源压缩窗口
class ResCompressPageWnd(QMainWindow, Ui_ResCompressWnd):
    mapping_dict = {}
    rc2zip = ResourceCompressToZip()
    def __init__(self, parent=None):
        super(ResCompressPageWnd, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        self.rc2zip.analyse_config()
        self.initUIMapping()
        self.initUI()


    def initUIMapping(self):
        self.mapping_dict[1] = [self.cb_0_0, self.lb_0_0]
        self.mapping_dict[2] = [self.cb_0_1, self.lb_0_1]
        self.mapping_dict[3] = [self.cb_0_2, self.lb_0_2]
        self.mapping_dict[4] = [self.cb_1_0, self.lb_1_0]
        self.mapping_dict[5] = [self.cb_1_1, self.lb_1_1]
        self.mapping_dict[6] = [self.cb_2_0, self.lb_2_0]
        self.mapping_dict[7] = [self.cb_3_0, self.lb_3_0]
        self.mapping_dict[8] = [self.cb_3_1, self.lb_3_1]
        self.mapping_dict[9] = [self.cb_3_2, self.lb_3_2]
        self.mapping_dict[10] = [self.cb_3_3, self.lb_3_3]
        self.mapping_dict[11] = [self.cb_4_0, self.lb_4_0]
        self.mapping_dict[12] = [self.cb_4_1, self.lb_4_1]
        self.mapping_dict[13] = [self.cb_4_2, self.lb_4_2]
        self.mapping_dict[14] = [self.cb_4_3, self.lb_4_3]


    def initUI(self):
        self.btn_zip_folder.clicked.connect(lambda: self.onZipFolderButtonClicked())
        self.btn_log_folder.clicked.connect(lambda: self.onLogFolderButtonClicked())
        self.btn_path_config.clicked.connect(lambda: self.onZipConfButtonClicked())
        self.btn_config_refresh.clicked.connect(self.onConfRefreshButtonClicked)
        self.btn_compress.clicked.connect(self.onResourceCompressButtonClicked)
        self.btn_clr_output.clicked.connect(self.onClearOutputPrintButtonClicked)
        self.cb_0_0.toggled.connect(lambda: self.onToggleChecked(1,self.cb_0_0))
        self.cb_0_1.toggled.connect(lambda: self.onToggleChecked(2,self.cb_0_1))
        self.cb_0_2.toggled.connect(lambda: self.onToggleChecked(3,self.cb_0_2))
        self.cb_1_0.toggled.connect(lambda: self.onToggleChecked(4,self.cb_1_0))
        self.cb_1_1.toggled.connect(lambda: self.onToggleChecked(5,self.cb_1_1))
        self.cb_2_0.toggled.connect(lambda: self.onToggleChecked(6,self.cb_2_0))
        self.cb_3_0.toggled.connect(lambda: self.onToggleChecked(7,self.cb_3_0))
        self.cb_3_1.toggled.connect(lambda: self.onToggleChecked(8,self.cb_3_1))
        self.cb_3_2.toggled.connect(lambda: self.onToggleChecked(9,self.cb_3_2))
        self.cb_3_3.toggled.connect(lambda: self.onToggleChecked(10,self.cb_3_3))
        self.cb_4_0.toggled.connect(lambda: self.onToggleChecked(11,self.cb_4_0))
        self.cb_4_1.toggled.connect(lambda: self.onToggleChecked(12,self.cb_4_1))
        self.cb_4_2.toggled.connect(lambda: self.onToggleChecked(13,self.cb_4_2))
        self.cb_4_3.toggled.connect(lambda: self.onToggleChecked(14,self.cb_4_3))

        self.loadConf2UI()


    # 加载配置文件内容至UI中的CheckBox
    def loadConf2UI(self):
        self.rc2zip.config_load()
        self.rc2zip.analyse_config()
        for index in self.rc2zip.config_dict:
            if not index in self.mapping_dict:
                continue
            self.mapping_dict[index][0].setChecked(self.rc2zip.config_dict[index]["isCompress"])
            self.mapping_dict[index][1].setText(self.rc2zip.config_dict[index]["last_output_time"])


    # 打开导出目录按钮响应
    def onZipFolderButtonClicked(self):
        self.thread = util.OpenByThread(zip_path)
        self.thread.start()
        global resCompressWnd


    # 打开日志目录按钮响应
    def onLogFolderButtonClicked(self):
        self.thread = util.OpenByThread(log_path)
        self.thread.start()


    # 打开配置按钮响应
    def onZipConfButtonClicked(self):
        self.thread = util.OpenByThread(zip_conf_path)
        self.thread.start()
    

    # 刷新配置表按钮响应
    def onConfRefreshButtonClicked(self):
        self.loadConf2UI()


    # 生成压缩包按钮响应
    def onResourceCompressButtonClicked(self):
        try:
            self.thread = ResourceCompressToZip()

            # 连接信号和槽
            self.thread.finished_signal.connect(self.resourseCompressFinished)
            self.thread.log_signal.connect(self.log_message)

            self.thread.start()

            # 操作进行中时屏蔽额外操作
            self.btn_compress.setEnabled(False)
            self.btn_config_refresh.setEnabled(False)
            self.btn_path_config.setEnabled(False)
            for index in self.mapping_dict:
                self.mapping_dict[index][0].setEnabled(False)
        except Exception as e:
            print(f"未处理的异常：{e}")


    # 压缩操作完成后
    def resourseCompressFinished(self):
        self.btn_compress.setEnabled(True)
        self.btn_config_refresh.setEnabled(True)
        self.btn_path_config.setEnabled(True)
        for index in self.mapping_dict:
            self.mapping_dict[index][0].setEnabled(True)
        self.loadConf2UI()


    # 清空日志按钮响应
    def onClearOutputPrintButtonClicked(self):
        self.t_output_print.setText("")


    # 多选框点击响应(同步更新配置csv表格)
    def onToggleChecked(self, index, check_box:QtWidgets.QCheckBox):
        try:
            if not index in self.rc2zip.config_dict:
                print("Error")
                return
            if check_box.isChecked():
                self.rc2zip.config_edit(index, 2, 1, config_csv_path, True)
            else:
                self.rc2zip.config_edit(index, 2, 0, config_csv_path, True)
        except Exception as e:
            util.warningMsgBox("提示","配置文件可能正在被占用，操作未生效")
            self.loadConf2UI()


    def log_message(self, message):
        # 将消息追加到文本浏览器中
        self.t_output_print.append(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建一个QApplication，也就是你要开发的软件app
    homeWnd = HomePageWindow()  # 创建一个QMainWindow，用来装载你需要的各种组件、控件
    resCompressWnd = ResCompressPageWnd()

    homeWnd.show()  # 执行QMainWindow的show()方法，显示这个QMainWindow
    
    sys.exit(app.exec_())  # 使用exit()或者点击关闭按钮退出QApp


# pyinstaller打包时使用的指令：（位于data目录时，选择正确的pyinstaller.exe）
# pyinstaller --onefile --noconsole --icon=UI/icon_designSimpleTool.ico --name=简易工具集 --distpath=dist --clean call_designSimpleTool.py