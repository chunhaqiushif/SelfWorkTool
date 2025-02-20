import os
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QUrl, Qt
from PyQt5.QtGui import QBrush, QColor, QDesktopServices,QFont
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QAbstractItemView, QFileIconProvider, QMenu, QTableWidget, QFrame, QTabWidget, QWidget
import qtawesome as qta
sys.path.append(os.path.join(os.path.abspath("."), "mainWnd\\UI"))
from mainWnd.UI.ui_designSimpleTool import Ui_MainWnd
import util.util_tool as util
from mainWnd.addons_import import AddonsLoad

global GMCode
GMCode = {}

root_path = os.path.abspath('.')
config_path = root_path + "\\" + "config"
gmcode_txt_path = config_path + "\\" + "gmcode.txt"
custom_dir_conf = config_path + "\\" + "customDirConf.json"
setting_conf = config_path + "\\" + "setting.json"
addons_path = root_path + "\\" + "addons"


# 主窗口
class HomePageWindow(QMainWindow, Ui_MainWnd):
    def __init__(self, parent=None):
        super(HomePageWindow, self).__init__(parent)
        self.setting_dict = {}
        self.tab_names = []
        self.tab_lists = []
        self.tab_count = 0
        self.all_conf_arr = []
        self.addon_tool = AddonsLoad()
        self.setupUi(self)          # 装载UI
        self.initSetting()          # 初始化设置
        # self.initGMCode()         # 初始化GM搜索
        self.initUI()               # 初始化UI事件
        self.initJumplistConfig()   # 初始化跳转列表配置文件
        self.initTab()              # 初始化选项卡内容
        self.initOtherTools()       # 初始化附加工具

        # 用于判断设置、附加工具栏是否展开的参数
        global is_setting_show
        is_setting_show = False
        global is_addon_tools_show
        is_addon_tools_show = False


    # 初始化附加工具
    def initOtherTools(self):
        self.addon_tool.load_all_module(self)


    # 初始化设置选项
    def initSetting(self):
        self.setting_dict = util.json_load(setting_conf)
        isTop = self.setting_dict["top_window"]
        isTrct = self.setting_dict["translucent"]
        self.load_wnd_setting_by_param(isTop, isTrct)
        self.cb_topThisWindow.setChecked(isTop)
        self.cb_translucentThisWindow.setChecked(isTrct)


    # 根据参数设置顶置和透明度
    def load_wnd_setting(self):
        self.setting_dict = util.json_load(setting_conf)
        self.load_wnd_setting_by_param(self.setting_dict["top_window"], self.setting_dict["translucent"])


    # 根据参数设置顶置和透明度
    def load_wnd_setting_by_param(self, top_window, translucent):
        # 顶置设置
        if top_window:
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.Widget)
        # 透明度设置
        if translucent:
            self.setWindowOpacity(0.75)
        else:
            self.setWindowOpacity(1)


    # 初始化UI
    def initUI(self):
        # self.btn_submitToSearch.setIcon(qta.icon('fa.search'))
        # self.btn_submitToSearch.clicked.connect(self.onSearchKeyClicked)

        # self.le_consoleCodeSearch.textChanged.connect(self.onGMCodeSearch)

        # self.btn_consoleCodeCopy.setIcon(qta.icon('fa5.copy'))
        # self.btn_consoleCodeCopy.clicked.connect(self.onGMCodeCopy)

        self.btn_pathSetting.setIcon(qta.icon('fa.folder-open'))
        self.btn_pathSetting.clicked.connect(self.onPathSettingClick)

        self.btn_quickJumpReload.setIcon(qta.icon('fa.refresh'))
        self.btn_quickJumpReload.clicked.connect(self.onQuickJumpReloadClick)

        self.btn_quickJump.setIcon(qta.icon('fa.play-circle-o'))
        self.btn_quickJump.clicked.connect(self.onQuickJumpClick)

        # self.tw_jumpListTable.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.tw_jumpListTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.onQuickJumpReloadClick()

        self.btn_svnSubmit.setIcon(qta.icon('fa.cloud-upload'))
        self.btn_svnSubmit.clicked.connect(self.onCommitDataclicked)

        self.btn_svnUpdata.setIcon(qta.icon('fa.cloud-download'))
        self.btn_svnUpdata.clicked.connect(self.onUpdataDataclicked)

        self.btn_setting.setIcon(qta.icon('fa.cog'))
        self.btn_setting.clicked.connect(self.onOpenSettingWndClicked)

        self.btn_other_tools.setIcon(qta.icon('fa5s.toolbox'))
        self.btn_other_tools.clicked.connect(self.onOpenAddonToolsWndClicked)

        self.cb_topThisWindow.toggled.connect(self.onTopThisWindowClicked)
        self.cb_translucentThisWindow.toggled.connect(self.onTranslucentThisWndClicked)

        self.btn_pathConfig.setIcon(qta.icon('fa.slack'))
        self.btn_pathConfig.clicked.connect(self.onPathConfigOpenClicked)

        # self.btn_consoleCode.setIcon(qta.icon('fa.slack'))
        # self.btn_consoleCode.clicked.connect(self.onGMCodeFileOpenClicked)
        
        self.btn_otherToolsPath.setIcon(qta.icon('fa.folder-open'))
        self.btn_otherToolsPath.clicked.connect(self.onOpenAddonToolsPathClicked)

        

        self.lb_coderSign.linkActivated.connect(self.open_gitHub_link)
        self.lb_coderSign_2.linkActivated.connect(self.open_gitHub_link)

        self.vl_other_tool_contents.setAlignment(Qt.AlignTop)

        self.setFixedSize(270, 825)


    # 创建新的QTableWidget
    def create_new_jumpList(self, parent_obj):
        tw_jumpListTable = QTableWidget(parent_obj)
        tw_jumpListTable.setEnabled(True)
        tw_jumpListTable.setGeometry(QtCore.QRect(0, 0, 245, 636))
        tw_jumpListTable.setMaximumSize(QtCore.QSize(250, 16777215))
        tw_jumpListTable.setSizeIncrement(QtCore.QSize(250, 0))
        font = QFont()
        font.setFamily("宋体")
        tw_jumpListTable.setFont(font)
        tw_jumpListTable.setStyleSheet("QTableWidget {\n"
"    background-color: rgba(255, 255, 255, 128);\n"
"    gridline-color: rgba(220, 220, 220, 150);\n"
"}\n"
"QTableWidget::item:selected {\n"
"    background-color: rgba(0, 85, 255, 200);\n"
"    border: 1px solid;\n"
"    border-color: rgba(0, 85, 255, 200);\n"
"}\n"
"\n"
"\n"
"QScrollBar:vertical {\n"
"    background: transparent;\n"
"    width: 10px; /* 可以根据需要调整滚动条宽度 */\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: #aaaaaa; /* 滚动条手柄颜色，可以根据需要调整 */\n"
"    border-radius: 4px; /* 滚动条手柄边框圆角，可以根据需要调整 */\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical,\n"
"QScrollBar::sub-line:vertical {\n"
"    height: 0; /* 隐藏滚动条的上下按钮 */\n"
"}\n"
"")
        tw_jumpListTable.setFrameShape(QFrame.NoFrame)
        tw_jumpListTable.setLineWidth(1)
        tw_jumpListTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        tw_jumpListTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        tw_jumpListTable.setAutoScroll(False)
        tw_jumpListTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tw_jumpListTable.setDragDropOverwriteMode(False)
        tw_jumpListTable.setTextElideMode(QtCore.Qt.ElideNone)
        tw_jumpListTable.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        tw_jumpListTable.setWordWrap(False)
        tw_jumpListTable.setRowCount(0)
        tw_jumpListTable.setColumnCount(3)
        item = QTableWidgetItem()
        tw_jumpListTable.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        tw_jumpListTable.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        tw_jumpListTable.setHorizontalHeaderItem(2, item)
        tw_jumpListTable.horizontalHeader().setVisible(False)
        tw_jumpListTable.horizontalHeader().setStretchLastSection(True)
        tw_jumpListTable.verticalHeader().setVisible(False)
        tw_jumpListTable.verticalHeader().setDefaultSectionSize(20)
        tw_jumpListTable.horizontalHeader().setSectionsMovable(False)
        tw_jumpListTable.itemDoubleClicked.connect(self.onQuickJumpClick)

        tw_jumpListTable.setContextMenuPolicy(Qt.CustomContextMenu)
        tw_jumpListTable.customContextMenuRequested.connect(self.show_context_menu)

        tw_jumpListTable.setSelectionMode(QAbstractItemView.SingleSelection)
        tw_jumpListTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        return tw_jumpListTable


    # 选项卡初始化
    def initTab(self):
        for tab_index in range(0, self.tab_count):
            tab_name = self.tab_names[tab_index]
            tab_list = self.tab_lists[tab_index]

            page = QWidget()
            self.tbw_jumpList.addTab(page, tab_name)
            tw_jumplist = self.create_new_jumpList(page)
            self.load_jump_list(tw_jumplist, tab_list)
            
            # 调整表格列宽
            tw_jumplist.resizeColumnToContents(1)
            tw_jumplist.setColumnWidth(0, 24)
            avg_width = 250
            tw_jumplist.setColumnWidth(2, avg_width - tw_jumplist.columnWidth(1) - 25)


    # 初始化跳转列表的配置信息
    def initJumplistConfig(self):
        self.all_conf_arr = util.json_load(custom_dir_conf)
        self.tab_names.clear()
        self.tab_lists.clear()
        self.tab_count = len(self.all_conf_arr)
        for tab_dict in self.all_conf_arr:
            self.tab_names.append(tab_dict["tab_text"])
            self.tab_lists.append(tab_dict["list"])


    # # 初始化GM代码
    # def initGMCode(self):
    #     global GMCode
    #     GMCodeFile = open(gmcode_txt_path, 'r', encoding='utf-8')
    #     for line in GMCodeFile:
    #         temp = line.split(":", 1)
    #         GMCode.update({temp[0]: temp[1].replace("\n", "")})
    #     GMCodeFile.close()


    # 获取当前tab中jumpList
    def get_cur_jumplist(self):
        tbw = self.tbw_jumpList.currentWidget()
        tw:QTableWidget = tbw.findChild(QTableWidget)
        return tw


    # 获取当前tab中jumpList所选的item
    def get_cur_jumplist_selected_items(self):
        tw:QTableWidget = self.get_cur_jumplist()
        items = tw.selectedItems()
        return items

    
    @pyqtSlot()
    # ※根据选中行打开对应路径下的文件夹/文件
    def onQuickJumpClick(self):
        items = self.get_cur_jumplist_selected_items()
        if len(items) != 0:
            self.onRunFileOrFolder(items[3].text())


    # ※根据所选文件打开其所在文件夹
    def onRightClickOpenFolderFromFile(self):
        items = self.get_cur_jumplist_selected_items()
        if len(items) != 0:
            self.onRunFileOrFolder(os.path.dirname(items[3].text()))


    # ※创建针对文件的右键菜单
    def create_menu_to_file(self):
        context_menu = QMenu(self)
        items = self.get_cur_jumplist_selected_items()
        file_path = items[3].text()
        folder_icon = QFileIconProvider().icon(QFileIconProvider.Folder)
        file_icon = util.get_file_icon(file_path)

        # 添加菜单项
        run_file = context_menu.addAction("打开文件")
        run_file.setIcon(file_icon)
        run_file.triggered.connect(lambda: self.onRunFileOrFolder(file_path))

        open_folder_action = context_menu.addAction("打开文件夹")
        open_folder_action.setIcon(folder_icon)
        open_folder_action.triggered.connect(self.onRightClickOpenFolderFromFile)

        return context_menu


    # 创建针对文件夹的右键菜单
    def create_menu_to_folder(self):
        context_menu = QMenu(self)

        folder_icon = QFileIconProvider().icon(QFileIconProvider.Folder)
        # 添加菜单项
        open_folder_action = context_menu.addAction("打开文件夹")
        open_folder_action.setIcon(folder_icon)
        open_folder_action.triggered.connect(self.onRightClickOpenFolderFromFile)

        updata_svn_action = context_menu.addAction("更新SVN")
        updata_svn_action.setIcon(folder_icon)
        updata_svn_action.triggered.connect(self.onUpdataDataclicked)

        commit_svn_action = context_menu.addAction("提交SVN")
        commit_svn_action.setIcon(folder_icon)
        commit_svn_action.triggered.connect(self.onCommitDataclicked)

        show_svn_log_action = context_menu.addAction("显示SVN日志")
        show_svn_log_action.setIcon(folder_icon)
        show_svn_log_action.triggered.connect(self.onShowSVNLogClicked)

        return context_menu


    # ※显示右键菜单
    def show_context_menu(self, pos):
        items = self.get_cur_jumplist_selected_items()
        if len(items) != 0:
            if os.path.isfile(items[3].text()):
                menu = self.create_menu_to_file()
                global_pos = self.tw_jumpListTable.viewport().mapToGlobal(pos)
                menu.exec_(global_pos)
            elif os.path.isdir(items[3].text()):
                menu = self.create_menu_to_folder()
                global_pos = self.tw_jumpListTable.viewport().mapToGlobal(pos)
                menu.exec_(global_pos)


    # 加载单个选项卡内的跳转列表
    def load_jump_list(self, tw:QTableWidget, info_list:list):
        col_count = 4
        row_count = len(info_list)
        tw.setRowCount(row_count)
        tw.setColumnCount(col_count)

        # 置入信息和数据
        for r in range(row_count):
            error_mark = False
            for c in range(col_count):
                # 图标
                if c == 0:
                    tw.setItem(r, c, QTableWidgetItem(info_list[r]["name"]))
                    if os.path.isfile(info_list[r]["path"]):
                        # 路径是文件
                        file_icon = util.get_file_icon(info_list[r]["path"])
                        item = QTableWidgetItem()
                        item.setIcon(file_icon)
                        item.setTextAlignment(Qt.AlignVCenter)
                        tw.setItem(r, c, item)
                    elif os.path.isdir(info_list[r]["path"]):
                        # 路径是文件夹
                        folder_icon = QFileIconProvider().icon(QFileIconProvider.Folder)
                        item = QTableWidgetItem()
                        item.setIcon(folder_icon)
                        item.setTextAlignment(Qt.AlignVCenter)
                        tw.setItem(r, c, item)
                    else:
                        # 路径异常
                        error_mark = True
                        error_icon = qta.icon('msc.error') # fa.question-circle-o
                        item = QTableWidgetItem()
                        item.setIcon(error_icon)
                        item.setTextAlignment(Qt.AlignVCenter)
                        tw.setItem(r, c, item)
                # 描述
                elif c == 1:
                    name = info_list[r]["name"]
                    if error_mark:
                        name = "*" + name
                    tw.setItem(r, c, QTableWidgetItem(name))
                # 分组
                elif c == 2:
                    qtw_value = QTableWidgetItem(info_list[r]["des"])
                    # qtw_value.setTextAlignment(Qt.AlignCenter)
                    tw.setItem(r, c, qtw_value)
                # 路径（不显示）
                elif c == 3:
                    tw.setItem(r, c, QTableWidgetItem(info_list[r]["path"]))
                # 行背景颜色
                rgb_values = util.hex_to_rgb(info_list[r]["bg_color"])
                tw.item(r, c).setBackground(QBrush(QColor(rgb_values[0],rgb_values[1],rgb_values[2],200)))
                # 如果路径异常，文本显示为红色
                if error_mark:
                    tw.item(r, c).setForeground(QBrush(QColor(255, 0, 0, 250)))


    @pyqtSlot()
    # ※刷新.加载快速跳转列表和GM指令
    def onQuickJumpReloadClick(self, tw:QTableWidget, info_list):
        pass
        
        # # 重载GM指令文本文档的载入
        # self.initGMCode()


    @pyqtSlot()
    # 打开程序/目录
    def onRunFileOrFolder(self, runPath):
        if os.path.exists(runPath):
            # 创建新线程启动文件，避免卡住
            self.thread = util.OpenByThread(runPath)
            self.thread.start()
        else:
            util.warningMsgBox("提示", "找不到路径下的文件/文件夹")



    # @pyqtSlot()
    # # 搜索GM指令
    # def onGMCodeSearch(self):
    #     inputText = self.le_consoleCodeSearch.text()
    #     if inputText == "":
    #         self.le_consoleCodeSearchResult.setText("")
    #         return
    #     suggestions = []
    #     pattern = '.*?'.join(inputText)  # 模糊匹配
    #     regex = re.compile(pattern)
    #     for item in GMCode.keys():
    #         match = regex.search(item)
    #         if match:
    #             suggestions.append((len(match.group()), match.start(), item, GMCode[item]))
    #     suggestions = sorted(suggestions)
    #     outputText = ""
    #     for tip in suggestions:
    #         outputText = outputText + tip[2] + ":" + "<@" + tip[3] + "> "
    #     if outputText == "":
    #         outputText = "无匹配结果"
    #     self.le_consoleCodeSearchResult.setText(outputText)
    #     self.le_consoleCodeSearchResult.setCursorPosition(0)


    # @pyqtSlot()
    # # 复制GM指令首个搜索结果
    # def onGMCodeCopy(self):
    #     outputText = self.le_consoleCodeSearchResult.text()
    #     if outputText == "":
    #         return
    #     regex = "<(@.*?)>"
    #     firstMatch = re.search(regex, outputText)
    #     if firstMatch == None:
    #         return
    #     copy_text = firstMatch.group(1)
    #     if firstMatch is None:
    #         return
    #     else:
    #         ls = firstMatch.group(1).split(" ")
    #         if len(ls) > 1:
    #             copy_text = ls[0]
    #     pyperclip3.copy(copy_text)


    # @pyqtSlot()
    # # 启动FileLocatoer并在选择的文件夹中搜索字段
    # def onSearchKeyClicked(self):
    #     file_path = addons_path + "\\" + "fileLocatorPro\\FileLocatorPro_x86.exe"
    #     if not os.path.exists(file_path):
    #         util.warningMsgBox("提示", "FileLocator程序不存在\n\n文件正确路径：\n" + "\\addons\\FileLocatorPro\\FileLocatorPro_x86.exe")
    #         return
    #     inputText = self.le_inputSearchTextEditor.text()
    #     items = self.tw_jumpListTable.selectedItems()
    #     if len(items) != 0 and os.path.isdir(items[3].text()):
    #         searchPath = items[3].text()
    #     else:
    #         util.warningMsgBox("提示", "未选中目录或选中的并非文件夹\nFileLocator无法进行搜索")
    #         return
    #     if inputText == "":
    #         searchText = file_path
    #     else:
            
    #         searchText = '"%s" -r -d "%s" -c "%s"' % (file_path, searchPath, inputText)
    #         print(searchText)
    #     self.thread = util.RunCmdByThread(searchText)
    #     self.thread.start()


    @pyqtSlot()
    # ※SVN更新当前选中目录
    def onUpdataDataclicked(self):
        items = self.tw_jumpListTable.selectedItems()
        if not len(items) == 0:
            runPath = items[3].text()
            if os.path.exists(runPath) and os.path.isdir(runPath):
                self.SVNUpdataOrCommit(runPath, 'update')
            else:
                util.warningMsgBox("提示", "找不到路径下的文件夹或不是目录，更新失败")


    @pyqtSlot()
    # ※提交SVN当前选中目录
    def onCommitDataclicked(self):
        items = self.tw_jumpListTable.selectedItems()
        if not len(items) == 0:
            runPath = items[3].text()
            if os.path.exists(runPath) and os.path.isdir(runPath):
                self.SVNUpdataOrCommit(runPath, 'commit')
            else:
                util.warningMsgBox("提示", "找不到路径下的文件夹或不是目录，提交失败")


    @pyqtSlot()
    # SVN更新与提交，根据参数二决定执行类型
    def SVNUpdataOrCommit(self, runPath, operateCommand):
        drive = runPath.split(":", 1)[0]  # 获取盘符
        consoleText_1stPart = '%s: & cd %s & setlocal enabledelayedexpansion' % (drive, runPath)  # 拼接指令
        consoleText_2ndPart = '& TortoiseProc.exe /command:%s /path:"." /closeonend:0' % operateCommand
        consoleText = consoleText_1stPart + consoleText_2ndPart
        self.thread = util.RunCmdByThread(consoleText)
        self.thread.start()

    
    @pyqtSlot()
    # ※显示SVN日志
    def onShowSVNLogClicked(self):
        items = self.tw_jumpListTable.selectedItems()
        if not len(items) == 0:
            runPath = items[3].text()
            if os.path.exists(runPath) and os.path.isdir(runPath):
                self.SVNUpdataOrCommit(runPath, 'log')
            else:
                util.warningMsgBox("提示", "找不到路径下的文件夹或不是目录")


    @pyqtSlot()
    # 打开工具集目录
    def onPathSettingClick(self):
        self.thread = util.OpenByThread(root_path)
        self.thread.start()


    @pyqtSlot()
    # 展开设置内容
    def onOpenSettingWndClicked(self):
        global is_setting_show
        if not is_setting_show:
            self.setMinimumHeight(920)
            self.setMaximumHeight(920)
            is_setting_show = True
            self.btn_setting.setText("设置 ▼")
        else:
            self.setMinimumHeight(825)
            self.setMaximumHeight(825)
            is_setting_show = False
            self.btn_setting.setText("设置 ▲")


    @pyqtSlot()
    # 展开附加工具内容
    def onOpenAddonToolsWndClicked(self):
        global is_addon_tools_show
        if not is_addon_tools_show:
            self.setMinimumWidth(531)
            self.setMaximumWidth(531)
            is_addon_tools_show = True
            self.btn_other_tools.setText("其他工具 ►")
        else:
            self.setMinimumWidth(270)
            self.setMaximumWidth(270)
            is_addon_tools_show = False
            self.btn_other_tools.setText("其他工具 ◄")


    @pyqtSlot()
    # 置顶勾选框的响应
    def onTopThisWindowClicked(self):
        if self.cb_topThisWindow.isChecked():
            self.setting_dict["top_window"] = True
        else:
            self.setting_dict["top_window"] = False
        util.json_save(self.setting_dict, setting_conf)
        self.load_wnd_setting_by_param(self.setting_dict["top_window"], self.setting_dict["translucent"])
        self.show()
        for wnd in self.addon_tool.get_all_wnd():
            if wnd.isVisible():
                if hasattr(wnd, "load_wnd_setting_by_param"):
                    wnd.load_wnd_setting_by_param(self.setting_dict["top_window"], self.setting_dict["translucent"])
                wnd.show()
            else:
                wnd.load_wnd_setting_by_param(self.setting_dict["top_window"], self.setting_dict["translucent"])
            


    @pyqtSlot()
    # 半透明勾选框的响应
    def onTranslucentThisWndClicked(self):
        if self.cb_translucentThisWindow.isChecked():
            self.setting_dict["translucent"] = True
        else:
            self.setting_dict["translucent"] = False
        util.json_save(self.setting_dict, setting_conf)
        self.load_wnd_setting_by_param(self.setting_dict["top_window"], self.setting_dict["translucent"])
        self.show()
        for wnd in self.addon_tool.get_all_wnd():
            if wnd.isVisible():
                if hasattr(wnd, "load_wnd_setting_by_param"):
                    wnd.load_wnd_setting_by_param(self.setting_dict["top_window"], self.setting_dict["translucent"])
                wnd.show()
            else:
                wnd.load_wnd_setting_by_param(self.setting_dict["top_window"], self.setting_dict["translucent"])


    @pyqtSlot()
    # 打开路径配置表
    def onPathConfigOpenClicked(self):
        if not os.path.exists(custom_dir_conf):
            util.warningMsgBox("提示", "配置文件不存在")
            return
        self.thread = util.OpenByThread(custom_dir_conf)
        self.thread.start()


    # @pyqtSlot()
    # # 打开GM指令文件
    # def onGMCodeFileOpenClicked(self):
    #     if not os.path.exists(gmcode_txt_path):
    #         util.warningMsgBox("提示", "配置文件不存在")
    #         return
    #     self.thread = util.OpenByThread(gmcode_txt_path)
    #     self.thread.start()


    # 打开Github链接
    def open_gitHub_link(self, url):
        QDesktopServices.openUrl(QUrl(url))


    @pyqtSlot()
    # 打开附加工具目录
    def onOpenAddonToolsPathClicked(self):
        self.thread = util.OpenByThread(addons_path)
        self.thread.start()