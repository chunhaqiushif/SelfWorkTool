import sys
import mainWnd.call_designSimpleTool as mainWnd
import xlrd
from PyQt5.QtWidgets import QApplication, QMessageBox

def exception_hook(exctype, value, traceback):
    error_message = f"An unhandled exception occurred:\n{value}"
    QMessageBox.critical(None, "Error", error_message, QMessageBox.Ok)
    sys.__excepthook__(exctype, value, traceback)

sys.excepthook = exception_hook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    homeWnd = mainWnd.HomePageWindow()
    homeWnd.show()
    
    sys.exit(app.exec_())


# pyinstaller打包时使用的指令：（位于data目录时，选择正确的pyinstaller.exe）
# pyinstaller --onefile --noconsole --icon=mainWnd/UI/icon_designSimpleTool.ico --exclude=addons --name=简易工具集 --distpath=dist --clean main.py