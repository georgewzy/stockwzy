


import mplfinance as mpf
import random
import time
import threading
import matplotlib.dates as mdates
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication,QWidget,QToolTip,QPushButton,QMessageBox,QDesktopWidget,QMainWindow,
                             QVBoxLayout,QHBoxLayout,QGridLayout,QTextEdit,QLabel,QRadioButton,QCheckBox,
                             QLineEdit,QGroupBox,QSplitter)
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
from matplotlib.dates import  date2num, MinuteLocator, SecondLocator, DateFormatter



class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=75):
        #  style='charles'
        # figsize=(width, height)
        # dpi=dpi

        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        # self.fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes1 = self.fig.add_subplot(111)

        # self.axes1  = plt.subplot(211)
        # self.axes2 = plt.subplot(212, sharex=self.axes1)
        self.axes1 = self.fig.add_subplot(2, 1, 1)   # row = 2, col = 1, index = 1
        self.axes2 = self.fig.add_subplot(2, 1, 2)    # row = 3, col = 1, index = 3
        self.fig.subplots_adjust(bottom=0.2, wspace=0,hspace=0)
        # self.fig.subplots_adjust(wspace=0, hspace=0)
        #

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_figure_k_line(self, datas):

        self.axes1.clear()
        self.axes2.clear()


        mpf.plot(datas, ax=self.axes1, volume=self.axes2, type='candle', style=sty, show_nontrading=False, tight_layout=False,scale_padding=0.15)
        # self.axes1.xaxis_date()
        # plt.xticks(rotation=30)
        self.draw()

    def update_figure_clear_k_line(self):
        print("update_figure_clear")
        self.axes1.clear()
        self.axes2.clear()
        self.draw()


class Wave(QWidget):

    closed = pyqtSignal()
    updatedisTextRawSignal = pyqtSignal(str)


    def __init__(self,parent = None):
        super(Wave,self).__init__(parent)
        print("1111111111111")
        self.init()
        self.initEvent()
        self.show()

    def __del__(self):
        pass

    def init(self):
        self.resize(1000,800)
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.canvas = MyMplCanvas()
        self.mainLayout.addWidget(self.canvas)


    def initEvent(self):
        self.updatedisTextRawSignal.connect(self.updateTextRaw)




    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def updateTextRaw(self,frame):
        self.disTextRaw.setText(frame)

