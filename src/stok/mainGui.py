import sys, os

import numpy as np
import baostock as bs
import pandas as pd

import matplotlib
import mplfinance
import random

matplotlib.use('Qt5Agg')

import matplotlib.pyplot  as plt
import mplfinance as mpf

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# from matplotlib.dates import  date2num, MinuteLocator, SecondLocator, DateFormatter


from stok import parameters, autoUpdate
from stok.combobox import ComboBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QDesktopWidget, QMainWindow,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QLabel, QRadioButton, QCheckBox,
                             QLineEdit, QGroupBox, QSplitter, QLCDNumber, QFileDialog, QMenuBar, QTableView,
                             QDateTimeEdit, QHeaderView)
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QStandardItemModel, QStandardItem

try:
    import cPickle as pickle
except ImportError:
    import pickle
if sys.platform == "win32":
    import ctypes

# 设置基本参数
# type: candle, renko, ohlc, line
# 此处选择candle,即K线图
# mav(moving average):均线类型,此处设置7,30,60日线
# volume:布尔类型，设置是否显示成交量，默认False
# title:设置标题
# y_label:设置纵轴主标题
# y_label_lower:设置成交量图一栏的标题
# figratio:设置图形纵横比
# figscale:设置图形尺寸(数值越大图像质量越高)
kwargs = dict(
    type='candle',
    mav=(3, 7, 21),
    title='george',
    ylabel='OHLC Candles',
    ylabel_lower='Traded Volume',
    figratio=(5, 4),
    figscale=5
)

# 设置marketcolors
# up:设置K线线柱颜色，up意为收盘价大于等于开盘价
# down:与up相反，这样设置与国内K线颜色标准相符
# edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
# wick:灯芯(上下影线)颜色
# volume:成交量直方图的颜色
# inherit:是否继承，选填
mc = mpf.make_marketcolors(
    up='red',  # 上涨时为红色
    down='green',  # 下跌时为绿色
    edge='black',  # 隐藏K线边缘
    wick='i',  #
    volume='in',  # 成交量用同样的颜色
    inherit=True
)

# 设置图形风格
# gridaxis:设置网格线位置
# gridstyle:设置网格线线型
# y_on_right:设置y轴位置是否在右
sty = mpf.make_mpf_style(
    gridaxis='both',  # 设置网格
    gridstyle='-.',  #
    y_on_right=True,  #
    marketcolors=mc  #
)


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
        self.axes1 = self.fig.add_subplot(3, 1, 1)  # row = 2, col = 1, index = 1
        self.axes2 = self.fig.add_subplot(3, 1, 2)  # row = 3, col = 1, index = 3
        self.axes3 = self.fig.add_subplot(3, 1, 3)  # row = 3, col = 1, index = 3
        self.fig.subplots_adjust(bottom=0.2, wspace=0, hspace=0)
        # self.fig.subplots_adjust(wspace=0, hspace=0)
        #

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_figure_k_line(self, datas):
        # print("datas", datas)
        # mpf.figure(style='charles')
        self.axes1.clear()
        self.axes2.clear()

        # type='candle'， renko， line， ohlc
        # mav=(3,6)
        # type='candle'， renko， line， ohlc
        # show_nontrading=False 去除非交易日
        # style=s
        # volume=True
        mpf.plot(datas, ax=self.axes1, volume=self.axes2, type='candle', style=sty, show_nontrading=False,
                 tight_layout=False, scale_padding=0.15)
        # self.axes1.xaxis_date()
        # plt.xticks(rotation=30)
        self.draw()

    def update_figure_ex3(self, datas):
        self.axes3.clear()

    def update_figure_clear_k_line(self):
        print("update_figure_clear")
        self.axes1.clear()
        self.axes2.clear()
        self.draw()


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def update_figure_k(self):
        idf = pd.read_csv('data/SPY_20110701_20120630_Bollinger.csv', index_col=0, parse_dates=True)
        idf.shape
        idf.head(3)
        idf.tail(3)
        df = idf.loc['2011-07-01':'2011-12-30', :]

        # mpf.figure(style='charles', figsize=(7, 8))
        data = df.iloc[0:20]
        self.axes1.clear()
        self.axes2.clear()
        mpf.plot(data, style=sty, type='candle', tight_layout=True, scale_padding=0.25)
        self.draw()

    def update_figure_k_line(self, datas):
        print("datas", datas)
        # mpf.figure(style='charles')
        self.axes1.clear()
        self.axes2.clear()

        # type='candle'， renko， line， ohlc
        # mav=(3,6)
        # type='candle'， renko， line， ohlc
        # show_nontrading=False 去除非交易日
        # style=s
        # volume=True
        mpf.plot(datas, ax=self.axes1, volume=self.axes2, type='candle', style=sty, show_nontrading=False,
                 tight_layout=False, scale_padding=0.15)
        # self.axes1.xaxis_date()
        # plt.xticks(rotation=30)
        self.draw()

    def update_figure_clear_k_line(self):
        print("update_figure_clear")
        self.axes1.clear()
        self.axes2.clear()
        self.draw()


class Ui_MainWindow(object):

    def initWindow(self):
        QToolTip.setFont(QFont('王中亚', 10))
        # main layout
        frameWidget = QWidget()
        mainWidget = QSplitter(Qt.Horizontal)  # 分隔符创建 主分隔符
        frameLayout = QVBoxLayout()  # 垂直布局（QVBoxLayout）
        self.settingWidget = QWidget()  #
        self.settingWidget.setProperty("class", "settingWidget")
        self.receiveSendWidget = QSplitter(Qt.Vertical)  # 分隔符创建
        self.functionalWiget = QWidget()  # 右边隐藏窗口
        self.optional_stock_list_Wiget = QWidget()  # 右边窗口

        # 创建三个垂直布局（QVBoxLayout）
        settingLayout = QVBoxLayout()  # 最左侧
        figure_Layout = QVBoxLayout()  # 中间件区域
        optional_list_Layout = QVBoxLayout()  # 右边

        self.settingWidget.setLayout(settingLayout)
        self.receiveSendWidget.setLayout(figure_Layout)
        self.optional_stock_list_Wiget.setLayout(optional_list_Layout)
        # self.functionalWiget.setLayout(sendFunctionalLayout)

        # 创建主窗口
        mainLayout = QHBoxLayout()  # 水平布局（QHBoxLayout）
        mainLayout.addWidget(self.settingWidget)  # 嵌套布局
        mainLayout.addWidget(self.receiveSendWidget)
        mainLayout.addWidget(self.optional_stock_list_Wiget)
        ## 参数1为索引,参数2为比例,单独设置一个位置的比例无效
        mainLayout.setStretch(0, 2)
        mainLayout.setStretch(1, 10)
        mainLayout.setStretch(2, 2)
        mainLayout.setSpacing(0)  ### 设置间距为0
        menuLayout = QHBoxLayout()  # 水平布局
        mainWidget.setLayout(mainLayout)  # 分隔符
        frameLayout.addLayout(menuLayout)  #
        frameLayout.addWidget(mainWidget)  #
        frameWidget.setLayout(frameLayout)  #
        self.setCentralWidget(frameWidget)  #

        # option layout
        self.settings_button = QPushButton()
        self.skin_button = QPushButton("")
        self.wave_button = QPushButton("")
        self.about_button = QPushButton()
        self.functional_button = QPushButton()
        self.encodingCombobox = ComboBox()

        self.settings_button.setProperty("class", "menuItem1")
        self.skin_button.setProperty("class", "menuItem2")
        self.about_button.setProperty("class", "menuItem3")
        self.functional_button.setProperty("class", "menuItem4")
        self.wave_button.setProperty("class", "menuItem5")
        self.settings_button.setObjectName("menuItem")
        self.skin_button.setObjectName("menuItem")
        self.about_button.setObjectName("menuItem")
        self.functional_button.setObjectName("menuItem")
        self.wave_button.setObjectName("menuItem")
        menuLayout.addWidget(self.settings_button)
        menuLayout.addWidget(self.skin_button)
        menuLayout.addWidget(self.wave_button)
        menuLayout.addWidget(self.about_button)
        menuLayout.addStretch(100)
        menuLayout.addWidget(self.functional_button)

        # widgets serial settings
        stock_GroupBox = QGroupBox("条件")
        stock_statistics_GridLayout = QGridLayout()
        start_date_labek = QLabel("开始")
        end_date_label = QLabel("结束")
        close_date_label = QLabel("close")
        stock_code_label = QLabel("编码")
        stock_period_label = QLabel("周期")
        adjustflag_label = QLabel("价格")
        self.start_date_edit = QDateTimeEdit()
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(QtCore.QDate(2020, 1, 1))  # 设置日期
        self.end_date_edit = QDateTimeEdit()
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setDate(QtCore.QDate(2020, 1, 22))  # 设置日期
        self.close_date_edit = QDateTimeEdit()
        self.close_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.close_date_edit.setDate(QtCore.QDate(2020, 1, 22))  # 设置日期
        # # 指定当前地日期为控件的日期，注意没有指定时间
        # dateEdit = QDateTimeEdit(QDate.currentDate(), self)
        # # 指定当前地时间为控件的时间，注意没有指定日期
        # timeEdit = QDateTimeEdit(QTime.currentTime(), self)
        self.serialPortCombobox = ComboBox()
        self.serailBaudrateCombobox = ComboBox()
        self.time_period_combobox = ComboBox()
        self.time_period_combobox.addItem("5")
        self.time_period_combobox.addItem("15")
        self.time_period_combobox.addItem("30")
        self.time_period_combobox.addItem("60")
        self.time_period_combobox.addItem("d")
        self.time_period_combobox.setCurrentIndex(4)
        self.stock_code_lineEdit = QLineEdit()
        self.stock_code_lineEdit.setText("002789")
        # self.adjustflag_combobox = ComboBox()
        # self.adjustflag_combobox.addItem("1")
        # self.adjustflag_combobox.addItem("2")
        # self.adjustflag_combobox.addItem("3")
        # self.adjustflag_combobox.setCurrentIndex(1)
        self.adjustflag_LineEdit = QLineEdit()

        stock_statistics_GridLayout.addWidget(start_date_labek, 0, 0, 1, 1)
        stock_statistics_GridLayout.addWidget(self.start_date_edit, 0, 1, 1, 1)
        stock_statistics_GridLayout.addWidget(end_date_label, 1, 0)
        stock_statistics_GridLayout.addWidget(self.end_date_edit, 1, 1)
        stock_statistics_GridLayout.addWidget(stock_code_label, 2, 0)
        stock_statistics_GridLayout.addWidget(self.stock_code_lineEdit, 2, 1)
        stock_statistics_GridLayout.addWidget(stock_period_label, 3, 0)
        stock_statistics_GridLayout.addWidget(self.time_period_combobox, 3, 1)
        stock_statistics_GridLayout.addWidget(adjustflag_label, 4, 0, 1, 1)
        stock_statistics_GridLayout.addWidget(self.adjustflag_LineEdit, 4, 1, 1, 1)
        stock_statistics_GridLayout.addWidget(close_date_label, 5, 0, 1, 1)
        stock_statistics_GridLayout.addWidget(self.close_date_edit, 5, 1, 1, 1)
        stock_GroupBox.setLayout(stock_statistics_GridLayout)
        settingLayout.addWidget(stock_GroupBox)

        button_GroupBox = QGroupBox("按键")
        button_GridLayout = QGridLayout()
        self.km15_button = QPushButton("15")
        self.km30_button = QPushButton("30")
        self.kmd_button = QPushButton("d")
        self.kmb15_button = QPushButton("15b")
        self.kmb30_button = QPushButton("30b")
        self.kmbd_button = QPushButton("db")
        self.insert_optional_button = QPushButton("加自选")
        self.delete_optional_button = QPushButton("删除")
        self.sync_stock_data_button = QPushButton("同步")
        self.show_stock_data_button = QPushButton("显示")
        self.figure_stock_data_button = QPushButton("图形")
        button_GridLayout.addWidget(self.km15_button, 0, 0, 1, 1)
        button_GridLayout.addWidget(self.km30_button, 0, 1, 1, 1)
        button_GridLayout.addWidget(self.kmd_button, 0, 2, 1, 1)
        button_GridLayout.addWidget(self.kmb15_button, 1, 0, 1, 1)
        button_GridLayout.addWidget(self.kmb30_button, 1, 1, 1, 1)
        button_GridLayout.addWidget(self.kmbd_button, 1, 2, 1, 1)
        button_GridLayout.addWidget(self.insert_optional_button, 2, 0, 1, 1)
        button_GridLayout.addWidget(self.delete_optional_button, 2, 1, 1, 1)
        button_GridLayout.addWidget(self.sync_stock_data_button, 2, 2, 1, 1)
        button_GroupBox.setLayout(button_GridLayout)
        settingLayout.addWidget(button_GroupBox)

        # serial receive settings
        slope_GroupBox = QGroupBox("坡度")
        slope_GridLayout = QGridLayout()

        kline_Label = QLabel("KD")
        self.kline_LCDNumber = QLCDNumber()
        red_Label = QLabel("RD")
        self.red_LCDNumber = QLCDNumber()
        green_Label = QLabel("GD")
        self.green_LCDNumber = QLCDNumber()
        klinev_Label = QLabel("KDV")
        self.klinev_LCDNumber = QLCDNumber()
        redv_Label = QLabel("RDV")
        self.redv_LCDNumber = QLCDNumber()
        greenv_Label = QLabel("GDV")
        self.greenv_LCDNumber = QLCDNumber()

        k15line_Label = QLabel("K15")
        self.k15line_LCDNumber = QLCDNumber()
        red15_Label = QLabel("R15")
        self.red15_LCDNumber = QLCDNumber()
        green15_Label = QLabel("G15")
        self.green15_LCDNumber = QLCDNumber()
        k15linev_Label = QLabel("K15V")
        self.k15linev_LCDNumber = QLCDNumber()
        red15v_Label = QLabel("R15V")
        self.red15v_LCDNumber = QLCDNumber()
        green15v_Label = QLabel("G15V")
        self.green15v_LCDNumber = QLCDNumber()

        slope_GridLayout.addWidget(kline_Label, 0, 0, 1, 1)
        slope_GridLayout.addWidget(self.kline_LCDNumber, 0, 1, 1, 1)
        slope_GridLayout.addWidget(red_Label, 0, 2, 1, 1)
        slope_GridLayout.addWidget(self.red_LCDNumber, 0, 3, 1, 1)
        slope_GridLayout.addWidget(green_Label, 0, 4, 1, 1)
        slope_GridLayout.addWidget(self.green_LCDNumber, 0, 5, 1, 1)
        slope_GridLayout.addWidget(klinev_Label, 1, 0, 1, 1)
        slope_GridLayout.addWidget(self.klinev_LCDNumber, 1, 1, 1, 1)
        slope_GridLayout.addWidget(redv_Label, 1, 2, 1, 1)
        slope_GridLayout.addWidget(self.redv_LCDNumber, 1, 3, 1, 1)
        slope_GridLayout.addWidget(greenv_Label, 1, 4, 1, 1)
        slope_GridLayout.addWidget(self.greenv_LCDNumber, 1, 5, 1, 1)

        slope_GridLayout.addWidget(k15line_Label, 2, 0, 1, 1)
        slope_GridLayout.addWidget(self.k15line_LCDNumber, 2, 1, 1, 1)
        slope_GridLayout.addWidget(red15_Label, 2, 2, 1, 1)
        slope_GridLayout.addWidget(self.red15_LCDNumber, 2, 3, 1, 1)
        slope_GridLayout.addWidget(green15_Label, 2, 4, 1, 1)
        slope_GridLayout.addWidget(self.green15_LCDNumber, 2, 5, 1, 1)
        slope_GridLayout.addWidget(k15linev_Label, 3, 0, 1, 1)
        slope_GridLayout.addWidget(self.k15linev_LCDNumber, 3, 1, 1, 1)
        slope_GridLayout.addWidget(red15v_Label, 3, 2, 1, 1)
        slope_GridLayout.addWidget(self.red15v_LCDNumber, 3, 3, 1, 1)
        slope_GridLayout.addWidget(green15v_Label, 3, 4, 1, 1)
        slope_GridLayout.addWidget(self.green15v_LCDNumber, 3, 5, 1, 1)

        slope_GroupBox.setLayout(slope_GridLayout)
        settingLayout.addWidget(slope_GroupBox)

        # serial send settings
        serialSendSettingsGroupBox = QGroupBox("预留")
        serialSendSettingsLayout = QGridLayout()
        serialSendSettingsGroupBox.setLayout(serialSendSettingsLayout)
        settingLayout.addWidget(serialSendSettingsGroupBox)
        settingLayout.setStretch(0, 2)
        settingLayout.setStretch(1, 2)
        settingLayout.setStretch(2, 2)
        settingLayout.setStretch(4, 2)

        ########################## widgets receive and send area
        self.period_widget = QWidget()
        period_button_Layout = QHBoxLayout()  # 水平布局 放置周期按钮
        period_button_GridLayout = QGridLayout()
        period_button_GridLayout.setContentsMargins(0, 0, 0, 0)
        self.period_widget.setLayout(period_button_GridLayout)
        self.kclear_buttion = QPushButton("KC")
        self.kshow_buttion = QPushButton("KS")
        self.a15_buttion = QPushButton("15")
        self.a30_buttion = QPushButton("30")
        self.a60_buttion = QPushButton("60")
        self.ad_buttion = QPushButton("日")
        self.k15_buttion = QPushButton("K15")
        self.k30_buttion = QPushButton("K30")
        self.k60_buttion = QPushButton("K60")
        self.kd_buttion = QPushButton("K日")
        self.kk15_buttion = QPushButton("KK15")
        self.kk30_buttion = QPushButton("KK30")
        self.kk60_buttion = QPushButton("KK60")
        self.kkd_buttion = QPushButton("KK日")
        self.kkk15_buttion = QPushButton("KKk15")
        self.kkk30_buttion = QPushButton("KKk30")
        self.kkk60_buttion = QPushButton("KKk60")
        self.kkkd_buttion = QPushButton("KkK日")

        period_button_GridLayout.addWidget(self.kclear_buttion, 0, 16, 1, 1)
        period_button_GridLayout.addWidget(self.a15_buttion, 0, 0, 1, 1)
        period_button_GridLayout.addWidget(self.a30_buttion, 0, 1, 1, 1)
        period_button_GridLayout.addWidget(self.a60_buttion, 0, 2, 1, 1)
        period_button_GridLayout.addWidget(self.ad_buttion, 0, 3, 1, 1)
        period_button_GridLayout.addWidget(self.k15_buttion, 0, 4, 1, 1)
        period_button_GridLayout.addWidget(self.k30_buttion, 0, 5, 1, 1)
        period_button_GridLayout.addWidget(self.k60_buttion, 0, 6, 1, 1)
        period_button_GridLayout.addWidget(self.kd_buttion, 0, 7, 1, 1)
        period_button_GridLayout.addWidget(self.kk15_buttion, 0, 8, 1, 1)
        period_button_GridLayout.addWidget(self.kk30_buttion, 0, 9, 1, 1)
        period_button_GridLayout.addWidget(self.kk60_buttion, 0, 10, 1, 1)
        period_button_GridLayout.addWidget(self.kkd_buttion, 0, 11, 1, 1)
        period_button_GridLayout.addWidget(self.kkk15_buttion, 1, 0, 1, 1)
        period_button_GridLayout.addWidget(self.kkk30_buttion, 1, 1, 1, 1)
        period_button_GridLayout.addWidget(self.kkk60_buttion, 1, 2, 1, 1)
        period_button_GridLayout.addWidget(self.kkkd_buttion, 1, 3, 1, 1)
        period_button_GridLayout.addWidget(self.kshow_buttion, 1, 4, 1, 1)


        # period_button_GridLayout.addStretch(1)  # 间距

        # KKKKK
        self.kline_widget = QWidget()
        receive_layout = QHBoxLayout()
        self.kline_widget.setLayout(receive_layout)
        self.dc = MyMplCanvas(width=8, height=5, dpi=80)

        # receive_layout.addWidget(self.dc)
        receive_layout.addWidget(self.dc)
        # 表格
        self.model = QStandardItemModel(10, 18)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(
            ['周期', '开始', '结束', '周期数', '涨幅', '幅度', '总手', '平均', '阴线', '幅度', '阴手', '平阴', '阳线', '幅度', '阳手', '平阳', '平线',
             '平手'])
        # 实例化表格视图，设置模型为自定义的模型
        self.tableview = QTableView()
        self.tableview.setModel(self.model)
        self.tableview.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)  # 表头将自动根据整个行或者列的内容去调整表头单元格到最佳的大小。用户或者程序员通过代码都不能改变它的大小。
        # self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 表头将会调整单元格到可得的空间。用户或者程序员通过代码都不能改变它的大小。
        # self.tableview.verticalHeader().hide()

        figure_Layout.addWidget(self.period_widget)  # 上
        figure_Layout.addWidget(self.kline_widget)  # 中
        figure_Layout.addWidget(self.tableview)  # 下
        figure_Layout.setStretch(0, 0.5)  # 上边宽度
        figure_Layout.setStretch(1, 12)  # 中间宽度
        figure_Layout.setStretch(2, 4)  # 下边宽度

        ####### 右边
        self.optional_stock_model = QStandardItemModel(1, 2)
        # 设置水平方向四个头标签文本内容
        self.optional_stock_model.setHorizontalHeaderLabels(['编号', '名字'])
        # 实例化表格视图，设置模型为自定义的模型
        self.optional_stock_tableview = QTableView()
        self.optional_stock_tableview.setModel(self.optional_stock_model)
        # self.optional_stock_tableview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 表头将自动根据整个行或者列的内容去调整表头单元格到最佳的大小。用户或者程序员通过代码都不能改变它的大小。
        # self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 表头将会调整单元格到可得的空间。用户或者程序员通过代码都不能改变它的大小。
        self.optional_stock_tableview.verticalHeader().hide()

        self.startButton = QPushButton("开始")
        optional_list_Layout.addWidget(self.optional_stock_tableview)
        optional_list_Layout.addWidget(self.startButton)

        # main window
        self.statusBarStauts = QLabel()
        self.statusBarStauts.setMinimumWidth(80)
        self.statusBarStauts.setText("<font color=%s>%s</font>" % ("#008200", parameters.strReady))

        self.tcpBarStauts = QLabel()
        self.tcpBarStauts.setMinimumWidth(80)
        self.tcpBarStauts.setText("<font color=%s>%s</font>" % ("#008200", "TCP"))

        self.statusBarSendCount = QLabel(parameters.strSend + "(bytes): " + "0")
        self.statusBarReceiveCount = QLabel(parameters.strReceive + "(bytes): " + "0")

        self.statusBar().addWidget(self.statusBarSendCount, 3)
        self.statusBar().addWidget(self.statusBarReceiveCount, 10)
        self.statusBar().addWidget(self.statusBarStauts, 10)
        self.statusBar().addWidget(self.tcpBarStauts, 10)

        self.resize(1700, 800)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        # self.MoveToCenter()
        # self.setWindowTitle(COMTool.parameters.appName+" V"+str(helpAbout.versionMajor)+"."+str(helpAbout.versionMinor))
        icon = QIcon()

        # print("icon path:"+self.DataPath+"/"+parameters.appIcon)
        # icon.addPixmap(QPixmap(self.DataPath+"/"+parameters.appIcon), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap(parameters.appIcon), QIcon.Normal, QIcon.Off)

        self.setWindowIcon(icon)  # 设置icon
        self.setWindowTitle('测试')

        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("comtool")
        self.show()
        print("config file path:", parameters.configFilePath)



