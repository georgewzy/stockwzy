

import matplotlib as mpl
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

import ComTool.borker as bk

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        self.__del__
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        print("444444444")
        FigureCanvas.updateGeometry(self)
        self.ax.set_xlabel("time of data generator")
        self.ax.set_ylabel('random data value')
        self.ax.legend()
        self.ax.set_ylim(1, 100)
        print("1111111111111")
        xfmt = mdates.DateFormatter('%H:%M:%S')
        # self.ax.xaxis.set_major_locator(MinuteLocator())  # every minute is a major locator
        # self.ax.xaxis.set_minor_locator(SecondLocator([10, 20, 30, 40, 50]))  # every 10 second is a minor locator
        self.ax.xaxis.set_major_formatter(xfmt)  # tick label formatter
        self.curveObj = None  # draw object # draw object

    def __del__(self):
        pass

    def plot(self, datax, datay):
        if self.curveObj is None:
            # create draw object once
            self.curveObj, = self.ax.plot(np.array(datax), np.array(datay), 'r-')
            print(self.curveObj)
        else:
            self.curveObj.set_data(np.array(datax), np.array(datay))
            # update limit of X axis,to make sure it can move
            self.ax.set_xlim(datax[0], datax[-1])
        self.draw()

    def plotDate(self, datax, datay):
        if self.curveObj is None:
            # create draw object once
            self.curveObj = self.ax.plot_date(np.array(datax), np.array(datay), 'r-')
            print(self.curveObj)
        else:
            self.curveObj.set_data(np.array(datax), np.array(datay))
            # update limit of X axis,to make sure it can move
            self.ax.set_xlim(datax[0], datax[-1])
        self.draw()


class Wave(QWidget):

    closed = pyqtSignal()
    updatedisTextRawSignal = pyqtSignal(str)
    dataX= []
    dataY= []

    def __init__(self,parent = None):
        super(Wave,self).__init__(parent)
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
        self.initDataGenerator()

    def initEvent(self):
        self.updatedisTextRawSignal.connect(self.updateTextRaw)

    def initDataGenerator(self):
        self.tData = threading.Thread(name="dataGenerator", target=self.generateData)
        self.tData.start()

    def generateData(self):
        counter = 0
        while (True):
            # newData = random.randint(1, 100)
            queSize = bk.serailQueue.qsize()

            if queSize != 0:
                recvMsg = bk.serailQueue.get()

                bs = str(recvMsg, encoding="utf8")
                begin = bs.find('RPM=')
                end = bs.find('\n\r')
                print(int(bs[begin+4:end]))
            newData = int(bs[begin+4:end])
            newTime = date2num(datetime.now())

            self.dataX.append(newTime)
            self.dataY.append(newData)
            self.canvas.plot(self.dataX, self.dataY)
            # self.canvas.update_figure(self.dataX, self.dataY)
            if counter >= 100:
                self.dataX.pop(0)
                self.dataY.pop(0)
            else:
                counter += 1

            time.sleep(0.05)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def updateTextRaw(self,frame):
        self.disTextRaw.setText(frame)

