
import sys, os


from stok.tcpClinet import *

from stok import parameters, helpAbout, autoUpdate
from stok.combobox import ComboBox
from stok.mainGui import Ui_MainWindow
from stok.stock import SerialComm

#from COMTool.wave import Wave

from PyQt5.QtWidgets import (QApplication)

import threading


def main():

    app = QApplication(sys.argv)
    mainWindow = SerialComm(app)

    print("mainWindow.param.skin1", mainWindow.param.skin)

    if (mainWindow.param.skin == 1):  # light skin
        print("mainWindow_DataPath:", mainWindow.DataPath)
        file = open(mainWindow.DataPath + '/assets/qss/style.qss', "r")
    else:  # elif mainWindow.param == 2: # dark skin
        print("mainWindow.param.skin", mainWindow.param.skin)
        file = open(mainWindow.DataPath + '/assets/qss/style-dark.qss', "r")
    qss = file.read().replace("$DataPath", mainWindow.DataPath)
    app.setStyleSheet(qss)


    t = threading.Thread(target=mainWindow.autoUpdateDetect)
    t.setDaemon(True)
    t.start()

    t2 = threading.Thread(target=mainWindow.display_optional_stock_table)
    t2.setDaemon(True)
    t2.start()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

