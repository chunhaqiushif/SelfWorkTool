import os
import sys
from importlib import import_module
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QPushButton
import util.util_tool as util
import mainWnd.call_designSimpleTool as mainWnd
from collections import OrderedDict

root_path = os.path.abspath('.')
addons_path = os.path.join(root_path, "addons")
global all_wnd
all_wnd = []

class AddonsLoad():

    # 动态导入模块
    def dynamic_load_wnd_and_call(self, module_name, class_name, module_path):
        # 将模块目录添加进sys.path
        sys.path.append(module_path)
        # 导入
        module = import_module(module_name)
        # 获取类对象
        loaded_class = getattr(module, class_name)
        # 创建类的实例
        instance = loaded_class()
        return instance


    # 附加工具模块加载
    def load_all_module(self, mainWnd: mainWnd):
        btn_dict = {}   # {"1":[btn1,btn2]}
        # try:
        for root, dirs, files in os.walk(addons_path):
            # 获取当前遍历的深度
            current_depth = root[len(addons_path):].count(os.sep)
            if current_depth == 1:
                for file in files:
                    if os.path.basename(file) == "info.json":
                        info = util.json_load(os.path.join(root, file))
                        if not info["btn_create"]:
                            continue
                        # 创建按钮并等待置入容器
                        button = QPushButton(info["btn_name"])
                        button.setFixedHeight(30)
                        # 置入临时数组并排序
                        order = str(info["btn_order"])
                        if order in btn_dict.keys():
                            btn_dict[order].append(button)
                        else:
                            btn_dict[order] = [button]
                        # 加载相关模块并连接按钮响应回调
                        if not info["entry"] == "" and not info["module_name"] == "":
                            module_path = root
                            wnd = self.dynamic_load_wnd_and_call(info["module_name"], info["entry"], module_path)
                            icon = QIcon()
                            icon.addPixmap(QPixmap(":/icon/icon_designSimpleTool.ico"), QIcon.Normal, QIcon.Off)
                            wnd.setWindowIcon(icon)
                            button.clicked.connect(lambda _, btn_wnd=wnd, main_wnd=mainWnd: self.show_wnd(btn_wnd, main_wnd))
                            global all_wnd
                            all_wnd.append(wnd)
        # 按钮排序后置入容器
        sorted_dict = OrderedDict(sorted(btn_dict.items()))
        for key in sorted_dict.keys():
            for btn in btn_dict[key]:
                mainWnd.vl_other_tool_contents.addWidget(btn)
        # except Exception as e:
        #     util.warningMsgBox("提示","配置文件出错或可能正在被占用，操作未生效：\n%s"%(e))
        #     self.loadConf2UI()

    def get_all_wnd(self):
        return all_wnd


    # 鼠标点击事件
    def show_wnd(self, wnd, mainWnd):
        # 当窗口已经打开时置于最上
        if wnd.isVisible():
            wnd.activateWindow()
            return
        # 主窗口居中位置打开新窗口
        wnd.setGeometry(
                int(mainWnd.geometry().center().x() - wnd.width() / 2),
                int(mainWnd.geometry().center().y() - wnd.height() / 2),
                wnd.width(),
                wnd.height()
            )
        wnd.show()