#!/home/wzy/PycharmProjects/hamClinet/venv/bin/python3.5
import sys, os
import math

import numpy as np
import baostock as bs
import pandas as pd
import matplotlib.pylab as plt
import mplfinance as mpf
import matplotlib.animation as animation


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# from matplotlib.dates import  date2num, MinuteLocator, SecondLocator, DateFormatter
from  matplotlib.pylab import date2num

from stok.tcpClinet import *
from stok.stopThreading import *
from stok.database import *
from stok.wave import Wave

from stok import parameters, helpAbout, autoUpdate
from stok.combobox import ComboBox
from stok.mainGui import Ui_MainWindow

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QDesktopWidget, QMainWindow,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QLabel, QRadioButton, QCheckBox,
                             QLineEdit, QGroupBox, QSplitter, QFileDialog)
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QStandardItem, QBrush, QColor
import threading
import time
import datetime



try:
    import cPickle as pickle
except ImportError:
    import pickle



class MyClass(object):
    def __init__(self, arg):
        super(MyClass, self).__init__()
        self.arg = arg


class SerialComm(QMainWindow, Ui_MainWindow):
    receiveUpdateSignal = pyqtSignal(str)
    errorSignal = pyqtSignal(str)
    showSerialComboboxSignal = pyqtSignal()
    serialDisableSettingsSignal = pyqtSignal(bool)  #
    tcpDisableSettingsSignal = pyqtSignal(bool)
    isDetectSerialPort = False
    receiveCount = 0
    sendCount = 0
    isScheduledSending = False
    DataPath = "./"
    isHideSettings = False
    isHideFunctinal = True
    app = None
    isWaveOpen = False
    row_tableview = 0
    line_row_tableview = 0
    sql = SqliteHelper()

    def __init__(self, app):
        super().__init__()
        self.app = app

        pathDirList = sys.argv[0].replace("\\", "/").split("/")
        print("self.DataPath", pathDirList)
        pathDirList.pop()
        print("self.DataPath", self.DataPath)
        self.DataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
        if not os.path.exists(self.DataPath + "/" + parameters.strDataDirName):
            pathDirList.pop()
            self.DataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
        self.DataPath = (self.DataPath + "/" + parameters.strDataDirName).replace("\\", "/")

        self.initWindow()
        self.initTool()
        self.initEvent()
        self.programStartGetSavedParameters()
        # 默认隐藏右边
        self.isHideFunctinal = True
        self.hideFunctional()

    def __del__(self):
        pass

    def initTool(self):
        lg = bs.login()
        # 显示登陆返回信息
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)


    def initEvent(self):
        self.km15_button.clicked.connect(self.get_k15_history_data)
        self.km30_button.clicked.connect(self.get_k30_history_data)
        self.kmd_button.clicked.connect(self.get_kd_history_data)
        self.kmb15_button.clicked.connect(self.get_k15_history_data_b)
        self.kmb30_button.clicked.connect(self.get_k30_history_data_b)
        self.kmbd_button.clicked.connect(self.get_kd_history_data_b)
        self.insert_optional_button.clicked.connect(self.insert_optional_stock_table)
        self.delete_optional_button.clicked.connect(self.delete_optional_stock_table)
        self.sync_stock_data_button.clicked.connect(self.sync_data)
        self.show_stock_data_button.clicked.connect(self.show_kd_line)
        self.a15_buttion.clicked.connect(self.show_a15_line)
        self.a30_buttion.clicked.connect(self.show_a30_line)
        self.a60_buttion.clicked.connect(self.show_a30_line)
        self.ad_buttion.clicked.connect(self.show_ad_line)
        self.k15_buttion.clicked.connect(self.show_k15_line)
        self.k30_buttion.clicked.connect(self.show_k30_line)
        self.k60_buttion.clicked.connect(self.show_k15_line)
        self.kd_buttion.clicked.connect(self.show_kd_line)
        self.kk15_buttion.clicked.connect(self.show_kk15_line)
        self.kk30_buttion.clicked.connect(self.show_kk30_line)
        self.kk60_buttion.clicked.connect(self.show_kk15_line)
        self.kkd_buttion.clicked.connect(self.show_kkd_line)
        self.kclear_buttion.clicked.connect(self.clear_figure)
        self.kshow_buttion.clicked.connect(self.show_ks_line)
        self.kall_buttion.clicked.connect(self.show_ka_line)
        self.ktest_buttion.clicked.connect(self.show_kt_line)

        self.errorSignal.connect(self.errorHint)
        self.showSerialComboboxSignal.connect(self.showCombobox)
        self.settings_button.clicked.connect(self.showHideSettings)
        self.skin_button.clicked.connect(self.skinChange)
        self.wave_button.clicked.connect(self.openWaveDisplay)
        self.about_button.clicked.connect(self.showAbout)
        self.functional_button.clicked.connect(self.showHideFunctional)

        self.myObject = MyClass(self)
        slotLambda = lambda: self.indexChanged_lambda(self.myObject)
        self.serialPortCombobox.currentIndexChanged.connect(slotLambda)


    # @QtCore.pyqtSlot(str)
    def indexChanged_lambda(self, obj):
        mainObj = obj.arg
        # print("item changed:",mainObj.serialPortCombobox.currentText())
        self.serialPortCombobox.setToolTip(mainObj.serialPortCombobox.currentText())

    def insert_optional_stock_table(self):
        lg = bs.login()
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
        stock_code = self.stock_code_lineEdit.text()
        if stock_code[0] == '6':
            stock_code = 'sh.' + stock_code
        else:
            stock_code = 'sz.' + stock_code
        rs = bs.query_stock_basic(code = stock_code)
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        ind = data_list[0][0].find('.')
        stock_code = data_list[0][0][ind+1:]
        stock_name = data_list[0][1]
        self.sql.insert_stock('stock', stock_code, stock_name)


    def delete_optional_stock_table(self):
        stock_code = self.stock_code_lineEdit.text()
        name_day = 'k' + stock_code + '_d'
        name_15 = 'k' + stock_code + '_15'
        name_30 = 'k' + stock_code + '_30'
        self.sql.delete_stock('stock', stock_code)
        self.sql.delete_table(name_day)
        self.sql.delete_table(name_15)
        self.sql.delete_table(name_30)

    def display_optional_stock_table(self):
        res = self.sql.select_stock('stock')
        for i in range(len(res)):
            for j in range(len(res[i])):
                self.optional_stock_model.setItem(i, j, QStandardItem(res[i][j]))

    def show_kt_line(self):
        # 创建表
        res = self.sql.select_stock('stock')
        for i in range(len(res)):
            name_day = 'k' + res[i][0] + '_d'
            name_15 = 'k' + res[i][0] + '_15'
            name_30 = 'k' + res[i][0] + '_30'
            self.sql.create_day_kline_table(name_day)
            self.sql.create_minute_kline_table(name_15)
            self.sql.create_minute_kline_table(name_30)

        start_date = '2020-07-23'
        end_date = str(datetime.datetime.now().date())
        # 更新数据
        res = self.sql.select_stock('stock')
        for i in range(len(res)):
            stock_code = res[i][0]
            if stock_code[0] == '6':
                stock_code = 'sh.' + stock_code
            else:
                stock_code = 'sz.' + stock_code
            #对应的表
            name_day = 'k' + res[i][0] + '_d'
            name_15 = 'k' + res[i][0] + '_15'
            name_30 = 'k' + res[i][0] + '_30'
            #日线

            lg = bs.login()
            rd = bs.query_history_k_data_plus(stock_code,
                                              "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                              start_date=start_date, end_date=end_date,
                                              frequency="d",
                                              adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权

            data_list = []
            while (rd.error_code == '0') & rd.next():
                # 获取一条记录，将记录合并在一起
                data_list.append(rd.get_row_data())
            print("data_list", data_list)

            for i in range(len(data_list)):
                if i == 0:
                    self.sql.insert_day_kline_data(name_day, data_list[i][0], data_list[i][1], data_list[i][2],
                                                   data_list[i][3], data_list[i][4], data_list[i][5],
                                                   data_list[i][6], data_list[i][7], data_list[i][8],
                                                   data_list[i][9], data_list[i][10], data_list[i][11],
                                                   data_list[i][12], 0.0, 0.0)
                else:
                    amplitude = round((float(data_list[i][3]) - float(data_list[i][4])) / float(data_list[i-1][5]) * 100.0, 6)  # 计算价格振幅

                    # volumeChg =  round((float(data_list[i][7]) - float(data_list[i-1][7])) / float(data_list[i-1][7]) * 100.0, 6)  # 计算成交量涨幅
                    if float(data_list[i - 1][7]) == 0.0:
                        volumeChg = 0.0
                    else:
                        volumeChg = round((float(data_list[i][7]) - float(data_list[i-1][7])) / float(data_list[i-1][7]) * 100.0, 6)  # 计算成交量涨幅
                    # volumeChg = 0.0
                    self.sql.insert_day_kline_data(name_day, data_list[i][0], data_list[i][1], data_list[i][2],
                                                   data_list[i][3], data_list[i][4], data_list[i][5],
                                                   data_list[i][6], data_list[i][7], data_list[i][8],
                                                   data_list[i][9], data_list[i][10], data_list[i][11],
                                                   data_list[i][12], amplitude, volumeChg)



    def sync_data(self):
        # 创建表
        res = self.sql.select_stock('stock')
        for i in range(len(res)):
            name_day = 'k' + res[i][0] + '_d'
            name_15 = 'k' + res[i][0] + '_15'
            name_30 = 'k' + res[i][0] + '_30'
            self.sql.create_day_kline_table(name_day)
            self.sql.create_minute_kline_table(name_15)
            self.sql.create_minute_kline_table(name_30)

        start_date = '2019-01-01'
        end_date = str(datetime.datetime.now().date())
        # 更新数据
        res = self.sql.select_stock('stock')
        for i in range(len(res)):
            stock_code = res[i][0]
            if stock_code[0] == '6':
                stock_code = 'sh.' + stock_code
            else:
                stock_code = 'sz.' + stock_code
            #对应的表
            name_day = 'k' + res[i][0] + '_d'
            name_15 = 'k' + res[i][0] + '_15'
            name_30 = 'k' + res[i][0] + '_30'
            #日线
            stock = self.sql.get_all_data_of_stock(name_day, start_date, end_date)
            if stock == False or stock == []:
                last_date = start_date
            else:
                stock_dataframe = pd.DataFrame(stock)
                last_date = stock_dataframe.tail(1).iloc[0,0]

            if last_date != end_date:
                lg = bs.login()
                rd = bs.query_history_k_data_plus(stock_code,
                                                  "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                                  start_date=last_date, end_date=end_date,
                                                  frequency="d",
                                                  adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权

                data_list = []
                while (rd.error_code == '0') & rd.next():
                    # 获取一条记录，将记录合并在一起
                    data_list.append(rd.get_row_data())
                for i in range(len(data_list)):
                    if i == 0:
                        self.sql.insert_day_kline_data(name_day, data_list[i][0], data_list[i][1], data_list[i][2],
                                                       data_list[i][3], data_list[i][4], data_list[i][5],
                                                       data_list[i][6], data_list[i][7], data_list[i][8],
                                                       data_list[i][9], data_list[i][10], data_list[i][11],
                                                       data_list[i][12], 0.0, 0)
                    else:
                        amplitude = round((float(data_list[i][3]) - float(data_list[i][4])) / float(data_list[i-1][5]) * 100.0, 6)  # 计算价格振幅
                        # volumeChg =  round((float(data_list[i][7]) - float(data_list[i-1][7])) / float(data_list[i-1][7]) * 100.0, 6)  # 计算成交量涨幅
                        if float(data_list[i-1][7]) == 0.0:
                            volumeChg = 0.0
                        else:
                            volumeChg = round((float(data_list[i][7]) - float(data_list[i-1][7])) / float(data_list[i-1][7]) * 100.0, 6)  # 计算成交量涨幅
                        self.sql.insert_day_kline_data(name_day, data_list[i][0], data_list[i][1], data_list[i][2],
                                                       data_list[i][3], data_list[i][4], data_list[i][5],
                                                       data_list[i][6], data_list[i][7], data_list[i][8],
                                                       data_list[i][9], data_list[i][10], data_list[i][11],
                                                       data_list[i][12], amplitude, volumeChg)

            #15分钟线
            stock = self.sql.get_all_data_of_stock(name_15, start_date, end_date)
            if stock == False or stock == []:
                last_date = start_date
            else:
                stock_dataframe = pd.DataFrame(stock)
                last_date = stock_dataframe.tail(1).iloc[0, 0]
            if last_date != end_date:
                lg = bs.login()
                rs = bs.query_history_k_data_plus(stock_code,
                                                  "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                                  start_date=last_date, end_date=end_date,
                                                  frequency='15', adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    # 获取一条记录，将记录合并在一起
                    data_list.append(rs.get_row_data())
                for i in range(len(data_list)):
                    if i == 0:
                        self.sql.insert_minute_kline_data(name_15, data_list[i][0], data_list[i][1], data_list[i][2],
                                                      data_list[i][3], data_list[i][4], data_list[i][5],
                                                      data_list[i][6], data_list[i][7], data_list[i][8],
                                                      data_list[i][9], 0.0, 0.0, 0.0)
                    else:
                        amplitude = round((float(data_list[i][4]) - float(data_list[i][5])) / float(data_list[i - 1][6]) * 100.0, 6)  # 计算涨振幅
                        pctchg = round((float(data_list[i][6]) - float(data_list[i-1][6])) / float(data_list[i-1][6]) * 100.0, 6)
                        if float(data_list[i-1][7]) == 0.0:
                            volumeChg = 0.0
                        else:
                            volumeChg = round((float(data_list[i][7]) - float(data_list[i-1][7])) / float(data_list[i-1][7]) * 100.0, 6)  # 计算成交量涨幅
                        self.sql.insert_minute_kline_data(name_15, data_list[i][0], data_list[i][1], data_list[i][2],
                                                          data_list[i][3], data_list[i][4], data_list[i][5],
                                                          data_list[i][6], data_list[i][7], data_list[i][8],
                                                          data_list[i][9], pctchg, amplitude, volumeChg)


            # 30分钟线
            stock = self.sql.get_all_data_of_stock(name_30, start_date, end_date)
            if stock == False or stock == []:
                last_date = start_date
            else:
                stock_dataframe = pd.DataFrame(stock)
                last_date = stock_dataframe.tail(1).iloc[0, 0]
            if last_date != end_date:
                lg = bs.login()
                rs = bs.query_history_k_data_plus(stock_code,
                                                  "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                                  start_date=last_date, end_date=end_date,
                                                  frequency='30',
                                                  adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权
                date_list = []
                while (rs.error_code == '0') & rs.next():
                    # 获取一条记录，将记录合并在一起
                    date_list.append(rs.get_row_data())
                for i in range(len(date_list)):
                    if i == 0:
                        self.sql.insert_minute_kline_data(name_30, date_list[i][0], date_list[i][1], date_list[i][2],
                                                          date_list[i][3], date_list[i][4], date_list[i][5],
                                                          date_list[i][6], date_list[i][7], date_list[i][8],
                                                          date_list[i][9], 0.0, 0.0, 0)
                    else:
                        amplitude = round((float(date_list[i][4]) - float(date_list[i][5])) / float(date_list[i-1][6]) * 100.0, 6)  # 计算涨振幅
                        pctchg = round((float(date_list[i][6]) - float(date_list[i - 1][6])) / float(date_list[i-1][6]) * 100.0, 6) #计算涨跌幅
                        if float(data_list[i-1][7]) == 0.0:
                            volumeChg = 0.0
                        else:
                            volumeChg = round((float(data_list[i][7]) - float(data_list[i-1][7])) / float(data_list[i-1][7]) * 100.0, 6)  # 计算成交量涨幅
                        self.sql.insert_minute_kline_data(name_30, date_list[i][0], date_list[i][1], date_list[i][2],
                                                          date_list[i][3], date_list[i][4], date_list[i][5],
                                                          date_list[i][6], date_list[i][7], date_list[i][8],
                                                          date_list[i][9], pctchg, amplitude, volumeChg)

    def down_data(self):
        t = threading.Thread(target=self.sync_data)
        t.setDaemon(True)
        t.start()

    def show_ad_line(self):
        stock_code = self.stock_code_lineEdit.text()
        stock_code = 'k' + stock_code + '_d'
        start_date = '2019-01-01'
        end_date = str(datetime.datetime.now().date())
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Code', 'Open', 'High', 'Low', 'Close', 'Preclose', 'Volume', 'Amount', 'j', 'k', 'l', 'm' 'n', 'o'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')
        show_datas = stock_dataframe.tail(112)
        show_datas.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)


    def show_kd_line(self):
        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        stock_code = 'k' + stock_code + '_d'
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)

        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Code', 'Open', 'High', 'Low', 'Close', 'Preclose', 'Volume', 'Amount', 'Adjustflag', 'turn', 'tradestatus', 'pctChg', 'amplitude', 'volumeChg'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')

        stock_az = stock_dataframe['Close']
        x = np.arange(0, len(stock_az))
        y = np.array(stock_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.kline_LCDNumber.display(r)

        show_datas_red = stock_dataframe[(stock_dataframe['pctChg'] >= 0)].sort_values(by="Close", ascending=True)
        show_datas_green = stock_dataframe[(stock_dataframe['pctChg'] < 0)].sort_values(by="Close", ascending=False)
        show_datas = pd.concat([show_datas_red, show_datas_green] , axis=0)  #拼接
        ######################
        clsoe = self.close_date_edit.text()
        clsoe_price = self.sql.get_data_by_date(stock_code, clsoe)
        print("clsoe_price", clsoe_price)

        red_az =  show_datas_red['pctChg']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.red_LCDNumber.display(r)
        green_az = show_datas_green['pctChg']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        g = math.degrees(h)
        self.green_LCDNumber.display(g)
        show_datas.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)

    def show_kkd_line(self):
        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        stock_code = 'k' + stock_code + '_d'
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Code', 'Open', 'High', 'Low', 'Close', 'Preclose', 'Volume', 'Amount', 'Adjustflag', 'turn', 'tradestatus', 'pctChg', 'amplitude', 'volumeChg'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')

        show_datas_red = stock_dataframe[(stock_dataframe['pctChg'] >= 0)].sort_values(by="Volume", ascending=True)
        show_datas_green = stock_dataframe[(stock_dataframe['pctChg'] < 0)].sort_values(by="Volume", ascending=False)
        show_datas = pd.concat([show_datas_red, show_datas_green] , axis=0)  #拼接
        stock_az = stock_dataframe['volumeChg']
        x = np.arange(0, len(stock_az))
        y = np.array(stock_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.klinev_LCDNumber.display(r)
        red_az =  show_datas_red['volumeChg']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.redv_LCDNumber.display(r)
        green_az = show_datas_green['volumeChg']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        g = math.degrees(h)
        self.greenv_LCDNumber.display(g)
        show_datas.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)

    def show_a15_line(self):
        start_date = '2019-01-01'
        end_date = str(datetime.datetime.now().date())
        # start_date = self.start_date_edit.text()
        # end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        stock_code = 'k' + stock_code + '_15'
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Time', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'adjustflag', 'pctChg', 'amplitude', 'volumeChg'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')
        show_datas = stock_dataframe.tail(112)
        show_datas.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)

    def show_k15_line(self):
        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        stock_code = 'k' + stock_code + '_15'
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Time', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'adjustflag', 'pctChg', 'amplitude', 'volumeChg'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')
        show_datas_red = stock_dataframe[(stock_dataframe['pctChg'] >= 0)].sort_values(by="Close", ascending=True)
        show_datas_green = stock_dataframe[(stock_dataframe['pctChg'] < 0)].sort_values(by="Close", ascending=False)
        show_datas = pd.concat([show_datas_red, show_datas_green], axis=0)  # 拼接
        stock_az = stock_dataframe['Close']
        x = np.arange(0, len(stock_az))
        y = np.array(stock_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.k15line_LCDNumber.display(r)
        red_az = show_datas_red['Close']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.red15_LCDNumber.display(r)
        green_az = show_datas_green['Close']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        g = math.degrees(h)
        self.green15_LCDNumber.display(g)
        show_datas.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)

    def show_kk15_line(self):
        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        stock_code = 'k' + stock_code + '_15'
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Time', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'adjustflag', 'pctChg', 'amplitude', 'volumeChg'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')

        show_datas_red = stock_dataframe[(stock_dataframe['pctChg'] >= 0)].sort_values(by="Volume", ascending=True)
        show_datas_green = stock_dataframe[(stock_dataframe['pctChg'] < 0)].sort_values(by="Volume", ascending=False)
        show_datas = pd.concat([show_datas_red, show_datas_green], axis=0)  # 拼接
        stock_az = stock_dataframe['Volume']
        x = np.arange(0, len(stock_az))
        y = np.array(stock_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.k15linev_LCDNumber.display(r)
        red_az = show_datas_red['volumeChg']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        print("z[0]z[0]", z[0])
        h = math.atan(z[0])
        r = math.degrees(h)
        self.red15v_LCDNumber.display(r)
        green_az = show_datas_green['volumeChg']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        g = math.degrees(h)
        self.green15v_LCDNumber.display(g)
        show_datas.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)


    def show_a30_line(self):
        stock_code = self.stock_code_lineEdit.text()
        start_date = '2019-01-01'
        end_date = str(datetime.datetime.now().date())
        stock_code = 'k' + stock_code + '_30'
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Time', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'adjustflag', 'pctChg', 'amplitude', 'volumeChg'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')
        show_datas = stock_dataframe.tail(112)
        stock_dataframe.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)

    def show_k30_line(self):
        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        stock_code = 'k' + stock_code + '_30'
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Time', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume',
                                                       'Amount', 'adjustflag', 'pctChg'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')
        show_datas_red = stock_dataframe[(stock_dataframe['pctChg'] >= 0)].sort_values(by="Close", ascending=True)
        show_datas_green = stock_dataframe[(stock_dataframe['pctChg'] < 0)].sort_values(by="Close", ascending=False)
        show_datas = pd.concat([show_datas_red, show_datas_green], axis=0)  # 拼接
        red_az = show_datas_red['Close']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        r = math.degrees(z[0])
        self.red_LCDNumber.display(r)

        green_az = show_datas_green['Close']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        g = math.degrees(z[0])
        self.green_LCDNumber.display(g)

        show_datas.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)

    def show_kk30_line(self):
        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        stock_code = 'k' + stock_code + '_30'
        stock = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        stock_dataframe = pd.DataFrame(stock, columns=['Date', 'Time', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume',
                                                       'Amount', 'adjustflag', 'pctChg'])
        stock_dataframe['Date'] = pd.to_datetime(stock_dataframe['Date'], format='%Y-%m-%d')
        show_datas_red = stock_dataframe[(stock_dataframe['pctChg'] >= 0)].sort_values(by="Volume", ascending=True)
        show_datas_green = stock_dataframe[(stock_dataframe['pctChg'] < 0)].sort_values(by="Volume", ascending=False)
        show_datas = pd.concat([show_datas_red, show_datas_green], axis=0)  # 拼接
        red_az = show_datas_red['Volume']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        r = math.degrees(z[0])
        self.redb_LCDNumber.display(r)  # 放大100倍 显示方便

        green_az = show_datas_green['Volume']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        g = math.degrees(z[0])
        self.greenb_LCDNumber.display(g)  # 放大100倍 显示方便

        show_datas.set_index('Date', inplace=True)
        self.dc.update_figure_k_line(show_datas)

    def show_ks_line(self):
        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        stock_code_kd = 'k' + stock_code + '_d'
        stock_code_k15 = 'k' + stock_code + '_15'
        stock_code_k30 = 'k' + stock_code + '_30'
        stock_kd = self.sql.get_all_data_of_stock(stock_code_kd, start_date, end_date)
        stock_k15 = self.sql.get_all_data_of_stock(stock_code_k15, start_date, end_date)

        stock_dataframe_kd = pd.DataFrame(stock_kd, columns=['Date', 'Code', 'Open', 'High', 'Low', 'Close', 'Preclose', 'Volume', 'Amount', 'Adjustflag', 'turn', 'tradestatus', 'pctChg', 'amplitude', 'volumeChg'])
        stock_dataframe_k15 = pd.DataFrame(stock_k15, columns=['Date', 'Time', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'adjustflag', 'pctChg', 'amplitude', 'volumeChg'])
        show_datas_red = stock_dataframe_kd[(stock_dataframe_kd['pctChg'] >= 0)].sort_values(by="Close", ascending=True)
        show_datas_green = stock_dataframe_kd[(stock_dataframe_kd['pctChg'] < 0)].sort_values(by="Close", ascending=False)

        stock_az = stock_dataframe_kd['Close']
        x = np.arange(0, len(stock_az))
        y = np.array(stock_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.kline_LCDNumber.display(r)
        red_az = show_datas_red['pctChg']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.red_LCDNumber.display(r)
        green_az = show_datas_green['pctChg']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        g = math.degrees(h)
        self.green_LCDNumber.display(g)

        show_datas_red = stock_dataframe_kd[(stock_dataframe_kd['pctChg'] >= 0)].sort_values(by="Volume", ascending=True)
        show_datas_green = stock_dataframe_kd[(stock_dataframe_kd['pctChg'] < 0)].sort_values(by="Volume", ascending=False)
        stock_az = stock_dataframe_kd['volumeChg']
        x = np.arange(0, len(stock_az))
        y = np.array(stock_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.klinev_LCDNumber.display(r)
        red_az = show_datas_red['volumeChg']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.redv_LCDNumber.display(r)
        green_az = show_datas_green['volumeChg']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        g = math.degrees(h)
        self.greenv_LCDNumber.display(g)

        show_datas_red = stock_dataframe_k15[(stock_dataframe_k15['pctChg'] >= 0)].sort_values(by="Close", ascending=True)
        show_datas_green = stock_dataframe_k15[(stock_dataframe_k15['pctChg'] < 0)].sort_values(by="Close", ascending=False)
        stock_az = stock_dataframe_k15['Close']
        x = np.arange(0, len(stock_az))
        y = np.array(stock_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.k15line_LCDNumber.display(r)
        red_az = show_datas_red['Close']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.red15_LCDNumber.display(r)
        green_az = show_datas_green['Close']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        g = math.degrees(h)
        self.green15_LCDNumber.display(g)

        show_datas_red = stock_dataframe_k15[(stock_dataframe_k15['pctChg'] >= 0)].sort_values(by="Volume", ascending=True)
        show_datas_green = stock_dataframe_k15[(stock_dataframe_k15['pctChg'] < 0)].sort_values(by="Volume", ascending=False)
        stock_az = stock_dataframe_k15['Volume']
        x = np.arange(0, len(stock_az))
        y = np.array(stock_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        r = math.degrees(h)
        self.k15linev_LCDNumber.display(r)
        red_az = show_datas_red['volumeChg']
        x = np.arange(0, len(red_az))
        y = np.array(red_az)
        z = np.polyfit(x, y, 1)
        print("z[0]z[0]", z[0])
        h = math.atan(z[0])
        r = math.degrees(h)
        self.red15v_LCDNumber.display(r)
        green_az = show_datas_green['volumeChg']
        x = np.arange(0, len(green_az))
        y = np.array(green_az)
        z = np.polyfit(x, y, 1)
        h = math.atan(z[0])
        g = math.degrees(h)
        self.green15v_LCDNumber.display(g)


    def show_ka_line(self):
        start_date = self.start_date_edit.text()
        # end_date = self.end_date_edit.text()
        end_date = str(datetime.datetime.now().date())
        stock_code = self.stock_code_lineEdit.text()
        stock_code_kd = 'k' + stock_code + '_d'
        stock_code_k15 = 'k' + stock_code + '_15'
        stock_code_k30 = 'k' + stock_code + '_30'
        stock_kd = self.sql.get_all_data_of_stock(stock_code_kd, start_date, end_date)
        stock_k15 = self.sql.get_all_data_of_stock(stock_code_k15, start_date, end_date)

        stock_dataframe_kd = pd.DataFrame(stock_kd, columns=['Date', 'Code', 'Open', 'High', 'Low', 'Close', 'Preclose', 'Volume', 'Amount', 'Adjustflag', 'turn', 'tradestatus', 'pctChg', 'amplitude', 'volumeChg'])
        stock_dataframe_k15 = pd.DataFrame(stock_k15, columns=['Date', 'Time', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'adjustflag', 'pctChg', 'amplitude', 'volumeChg'])

        for i in range(len(stock_dataframe_kd)):
            print("i", i)
            stock_dataframe_kd = stock_dataframe_kd.head(i)

            show_datas_red = stock_dataframe_kd[(stock_dataframe_kd['pctChg'] >= 0)].sort_values(by="Close", ascending=True)
            show_datas_green = stock_dataframe_kd[(stock_dataframe_kd['pctChg'] < 0)].sort_values(by="Close", ascending=False)

            red_az = show_datas_red['pctChg']
            x = np.arange(0, len(red_az))
            y = np.array(red_az)
            z = np.polyfit(x, y, 1)
            h = math.atan(z[0])
            r = math.degrees(h)
            self.red_LCDNumber.display(r)
            green_az = show_datas_green['pctChg']
            x = np.arange(0, len(green_az))
            y = np.array(green_az)
            z = np.polyfit(x, y, 1)
            h = math.atan(z[0])
            g = math.degrees(h)
            self.green_LCDNumber.display(g)

        # show_datas_red = stock_dataframe_kd[(stock_dataframe_kd['pctChg'] >= 0)].sort_values(by="Volume", ascending=True)
        # show_datas_green = stock_dataframe_kd[(stock_dataframe_kd['pctChg'] < 0)].sort_values(by="Volume", ascending=False)
        # stock_az = stock_dataframe_kd['volumeChg']
        # x = np.arange(0, len(stock_az))
        # y = np.array(stock_az)
        # z = np.polyfit(x, y, 1)
        # h = math.atan(z[0])
        # r = math.degrees(h)
        # self.klinev_LCDNumber.display(r)
        # red_az = show_datas_red['volumeChg']
        # x = np.arange(0, len(red_az))
        # y = np.array(red_az)
        # z = np.polyfit(x, y, 1)
        # h = math.atan(z[0])
        # r = math.degrees(h)
        # self.redv_LCDNumber.display(r)
        # green_az = show_datas_green['volumeChg']
        # x = np.arange(0, len(green_az))
        # y = np.array(green_az)
        # z = np.polyfit(x, y, 1)
        # h = math.atan(z[0])
        # g = math.degrees(h)
        # self.greenv_LCDNumber.display(g)
        #
        # show_datas_red = stock_dataframe_k15[(stock_dataframe_k15['pctChg'] >= 0)].sort_values(by="Close", ascending=True)
        # show_datas_green = stock_dataframe_k15[(stock_dataframe_k15['pctChg'] < 0)].sort_values(by="Close", ascending=False)
        # stock_az = stock_dataframe_k15['Close']
        # x = np.arange(0, len(stock_az))
        # y = np.array(stock_az)
        # z = np.polyfit(x, y, 1)
        # h = math.atan(z[0])
        # r = math.degrees(h)
        # self.k15line_LCDNumber.display(r)
        # red_az = show_datas_red['Close']
        # x = np.arange(0, len(red_az))
        # y = np.array(red_az)
        # z = np.polyfit(x, y, 1)
        # h = math.atan(z[0])
        # r = math.degrees(h)
        # self.red15_LCDNumber.display(r)
        # green_az = show_datas_green['Close']
        # x = np.arange(0, len(green_az))
        # y = np.array(green_az)
        # z = np.polyfit(x, y, 1)
        # h = math.atan(z[0])
        # g = math.degrees(h)
        # self.green15_LCDNumber.display(g)
        #
        # show_datas_red = stock_dataframe_k15[(stock_dataframe_k15['pctChg'] >= 0)].sort_values(by="Volume", ascending=True)
        # show_datas_green = stock_dataframe_k15[(stock_dataframe_k15['pctChg'] < 0)].sort_values(by="Volume", ascending=False)
        # stock_az = stock_dataframe_k15['Volume']
        # x = np.arange(0, len(stock_az))
        # y = np.array(stock_az)
        # z = np.polyfit(x, y, 1)
        # h = math.atan(z[0])
        # r = math.degrees(h)
        # self.k15linev_LCDNumber.display(r)
        # red_az = show_datas_red['volumeChg']
        # x = np.arange(0, len(red_az))
        # y = np.array(red_az)
        # z = np.polyfit(x, y, 1)
        # print("z[0]z[0]", z[0])
        # h = math.atan(z[0])
        # r = math.degrees(h)
        # self.red15v_LCDNumber.display(r)
        # green_az = show_datas_green['volumeChg']
        # x = np.arange(0, len(green_az))
        # y = np.array(green_az)
        # z = np.polyfit(x, y, 1)
        # h = math.atan(z[0])
        # g = math.degrees(h)
        # self.green15v_LCDNumber.display(g)

    def clear_figure(self):
        print("show_figure")
        self.dc.update_figure_clear_k_line()


    def get_k15_history_data(self):
        volume_average = 0
        volume_total = 0
        volume_yang = 0
        volume_yin = 0
        volume_zero = 0
        volume_yang_b = 0
        volume_yin_b = 0
        pctchg_amplitude = 0.0
        pctchg_total = 0.0
        pctchg_yang = 0.0
        pctchg_yin = 0.0
        line_count_zero = 0
        line_count_yang = 0
        line_count_yin = 0

        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        time_period = self.time_period_combobox.currentText()

        stock_code = 'k' + stock_code + '_15'
        print(stock_code)

        data_list = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        print(data_list)

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  #计算总成交量
            pctchg_total = pctchg_total + float(data_list[i][10])

            if float(data_list[i][10] == 0):
                volume_zero = volume_zero + int(data_list[i][7])
                line_count_zero += 1
            elif float(data_list[i][10] > 0):
                volume_yang = volume_yang + int(data_list[i][7])
                line_count_yang += 1
                pctchg_yang = pctchg_yang + float(data_list[i][10])
            else:
                volume_yin = volume_yin + int(data_list[i][7])
                line_count_yin += 1
                pctchg_yin = pctchg_yin + float(data_list[i][10])

        pctchg_amplitude = round(pctchg_yang + abs(pctchg_yin), 2)  # 振幅
        volume_average = round(volume_total / 100 / pctchg_amplitude)  # 平均
        volume_total = round(volume_total / 100)  #股数转手（1手=100）
        volume_yin = round(volume_yin / 100)
        volume_yang = round(volume_yang / 100)
        volume_zero = round(volume_zero / 100)
        volume_yin_b = round(abs(pctchg_yin) * volume_average)
        volume_yang_b = round(pctchg_yang * volume_average)

        line_tableview = 0
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem('15'))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(start_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(end_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(len(data_list))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_total, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(pctchg_amplitude)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_total)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_average)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yin, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(0, 255, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yang, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(255, 0, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_zero)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_zero)))
        self.row_tableview += 1

    def get_k15_history_data_b(self):
        volume_average = 0
        volume_total = 0
        volume_yang = 0
        volume_yin = 0
        volume_zero = 0
        volume_yang_b = 0
        volume_yin_b = 0
        pctchg_amplitude = 0.0
        pctchg_total = 0.0
        pctchg_yang = 0.0
        pctchg_yin = 0.0
        line_count_zero = 0
        line_count_yang = 0
        line_count_yin = 0

        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        time_period = self.time_period_combobox.currentText()

        stock_code = 'k' + stock_code + '_15'
        print(stock_code)

        data_list = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        print(data_list)

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  #计算总成交量
            pctChg = (float(data_list[i][6]) - float(data_list[i][3])) / float(data_list[i][3]) * 100
            pctchg_total = pctchg_total + float(pctChg)

            if pctChg == 0:
                print(data_list[i][1], pctChg)
                volume_zero = volume_zero + int(data_list[i][7])
                line_count_zero += 1
            elif pctChg > 0:
                volume_yang = volume_yang + int(data_list[i][7])
                line_count_yang += 1
                pctchg_yang = pctchg_yang + pctChg
            else:
                volume_yin = volume_yin + int(data_list[i][7])
                line_count_yin += 1
                pctchg_yin = pctchg_yin + pctChg

        pctchg_amplitude = round(pctchg_yang + abs(pctchg_yin), 2)  # 振幅
        volume_average = round(volume_total / 100 / pctchg_amplitude)  # 平均
        volume_total = round(volume_total / 100)  #股数转手（1手=100）
        volume_yin = round(volume_yin / 100)
        volume_yang = round(volume_yang / 100)
        volume_zero = round(volume_zero / 100)
        volume_yin_b = round(abs(pctchg_yin) * volume_average)
        volume_yang_b = round(pctchg_yang * volume_average)

        line_tableview = 0
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem('15b'))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(start_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(end_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(len(data_list))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_total, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(pctchg_amplitude)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_total)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_average)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yin, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(0, 255, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yang, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(255, 0, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_zero)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_zero)))
        self.row_tableview += 1

    def get_k30_history_data(self):
        volume_average = 0
        volume_total = 0
        volume_yang = 0
        volume_yin = 0
        volume_zero = 0
        volume_yang_b = 0
        volume_yin_b = 0
        pctchg_amplitude = 0.0
        pctchg_total = 0.0
        pctchg_yang = 0.0
        pctchg_yin = 0.0
        line_count_zero = 0
        line_count_yang = 0
        line_count_yin = 0

        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        time_period = self.time_period_combobox.currentText()

        stock_code = 'k' + stock_code + '_30'
        print(stock_code)

        data_list = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        print(data_list)


        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  # 计算总成交量
            pctchg_total = pctchg_total + float(data_list[i][10])

            if float(data_list[i][10] == 0):
                volume_zero = volume_zero + int(data_list[i][7])
                line_count_zero += 1
            elif float(data_list[i][10] > 0):
                volume_yang = volume_yang + int(data_list[i][7])
                line_count_yang += 1
                pctchg_yang = pctchg_yang + float(data_list[i][10])
            else:
                volume_yin = volume_yin + int(data_list[i][7])
                line_count_yin += 1
                pctchg_yin = pctchg_yin + float(data_list[i][10])


        pctchg_amplitude = round(pctchg_yang + abs(pctchg_yin), 2)  # 振幅
        volume_average = round(volume_total / 100 / pctchg_amplitude)  # 平均
        volume_total = round(volume_total / 100)
        volume_yin = round(volume_yin / 100)
        volume_yang = round(volume_yang / 100)
        volume_zero = round(volume_zero / 100)
        volume_yin_b = round(abs(pctchg_yin) * volume_average)
        volume_yang_b = round(pctchg_yang * volume_average)

        line_tableview = 0
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem('30'))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(start_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(end_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(len(data_list))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_total, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(pctchg_amplitude)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_total)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_average)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yin, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(0, 255, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yang, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(255, 0, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_zero)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_zero)))
        self.row_tableview += 1


    def get_k30_history_data_b(self):
        volume_average = 0
        volume_total = 0
        volume_yang = 0
        volume_yin = 0
        volume_zero = 0
        volume_yang_b = 0
        volume_yin_b = 0
        pctchg_amplitude = 0.0
        pctchg_total = 0.0
        pctchg_yang = 0.0
        pctchg_yin = 0.0
        line_count_zero = 0
        line_count_yang = 0
        line_count_yin = 0

        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        time_period = self.time_period_combobox.currentText()

        stock_code = 'k' + stock_code + '_30'
        print(stock_code)

        data_list = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        print(data_list)

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  # 计算总成交量
            pctChg = (float(data_list[i][6]) - float(data_list[i][3])) / float(data_list[i][3]) * 100.0
            pctchg_total = pctchg_total + float(pctChg)
            if pctChg == 0:
                print(data_list[i][1], pctChg)
                volume_zero = volume_zero + int(data_list[i][7])
                line_count_zero += 1
            elif pctChg > 0:
                volume_yang = volume_yang + int(data_list[i][7])
                line_count_yang += 1
                pctchg_yang = pctchg_yang + pctChg
            else:
                volume_yin = volume_yin + int(data_list[i][7])
                line_count_yin += 1
                pctchg_yin = pctchg_yin + pctChg

        pctchg_amplitude = round(pctchg_yang + abs(pctchg_yin), 2)  # 振幅
        volume_average = round(volume_total / 100 / pctchg_amplitude)  # 平均
        volume_total = round(volume_total / 100)
        volume_yin = round(volume_yin / 100)
        volume_yang = round(volume_yang / 100)
        volume_zero = round(volume_zero / 100)
        volume_yin_b = round(abs(pctchg_yin) * volume_average)
        volume_yang_b = round(pctchg_yang * volume_average)

        line_tableview = 0
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem('30b'))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(start_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(end_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(len(data_list))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_total, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(pctchg_amplitude)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_total)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_average)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yin, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(0, 255, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yang, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(255, 0, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_zero)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_zero)))
        self.row_tableview += 1

    def get_kd_history_data(self):
        volume_average = 0
        volume_total = 0
        volume_yang = 0
        volume_yin = 0
        volume_zero = 0
        volume_yang_b = 0
        volume_yin_b = 0
        pctchg_amplitude = 0.0
        pctchg_total = 0.0
        pctchg_yang = 0.0
        pctchg_yin = 0.0
        line_count_zero = 0
        line_count_yang = 0
        line_count_yin = 0
        line_tableview = 0

        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        time_period = self.time_period_combobox.currentText()
        stock_code = 'k' + stock_code + '_d'
        print(stock_code)

        data_list = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        print(data_list)

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  #总成交量
            pctchg_total = pctchg_total + float(data_list[i][12])#总涨幅

            if float(data_list[i][12] == 0):
                volume_zero = volume_zero + int(data_list[i][7])  #成交量
                line_count_zero += 1
            elif float(data_list[i][12]) > 0:
                volume_yang = volume_yang + int(data_list[i][7])
                line_count_yang += 1
                pctchg_yang = pctchg_yang + float(data_list[i][12])
            else:
                volume_yin = volume_yin + int(data_list[i][7])
                line_count_yin += 1
                pctchg_yin = pctchg_yin + float(data_list[i][12])


        pctchg_amplitude = round(pctchg_yang + abs(pctchg_yin), 2)  # 振幅
        volume_average = round(volume_total / 100 / pctchg_amplitude)  # 平均
        volume_total = round(volume_total / 100)
        volume_yin = round(volume_yin / 100)
        volume_yang = round(volume_yang / 100)
        volume_zero = round(volume_zero / 100)
        volume_yin_b = round(abs(pctchg_yin) * volume_average)
        volume_yang_b = round(pctchg_yang * volume_average)


        line_tableview = 0
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem('d'))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(start_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(end_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(len(data_list))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_total, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(pctchg_amplitude)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_total)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_average)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yin, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(0, 255, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yang, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(255, 0, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_zero)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_zero)))
        self.row_tableview += 1


    def get_kd_history_data_b(self):
        volume_average = 0
        volume_total = 0
        volume_yang = 0
        volume_yin = 0
        volume_zero = 0
        pctchg_amplitude = 0.0
        pctchg_total = 0.0
        pctchg_yang = 0.0
        pctchg_yin = 0.0
        line_count_zero = 0
        line_count_yang = 0
        line_count_yin = 0
        line_tableview = 0

        start_date = self.start_date_edit.text()
        end_date = self.end_date_edit.text()
        stock_code = self.stock_code_lineEdit.text()
        time_period = self.time_period_combobox.currentText()
        stock_code = 'k' + stock_code + '_d'
        print(stock_code)

        data_list = self.sql.get_all_data_of_stock(stock_code, start_date, end_date)
        print(data_list)

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])
            pctChg = (float(data_list[i][5]) - float(data_list[i][2])) / float(data_list[i][2]) * 100.0
            pctchg_total = pctchg_total + float(data_list[i][12])

            if pctChg == 0:
                volume_zero = volume_zero + int(data_list[i][7])
                line_count_zero += 1
            elif pctChg > 0:
                volume_yang = volume_yang + int(data_list[i][7])
                line_count_yang += 1
                pctchg_yang = pctchg_yang + float(data_list[i][12])
            else:
                volume_yin = volume_yin + int(data_list[i][7])
                line_count_yin += 1
                pctchg_yin = pctchg_yin + float(data_list[i][12])

        pctchg_amplitude = round(pctchg_yang + abs(pctchg_yin), 2)  # 振幅
        volume_average = round(volume_total / 100 / pctchg_amplitude)  # 平均
        volume_total = round(volume_total / 100)
        volume_yin = round(volume_yin / 100)
        volume_yang = round(volume_yang / 100)
        volume_zero = round(volume_zero / 100)
        volume_yin_b = round(abs(pctchg_yin) * volume_average)
        volume_yang_b = round(pctchg_yang * volume_average)

        line_tableview = 0
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem('d'))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(start_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(end_date))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(len(data_list))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_total, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(pctchg_amplitude)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_total)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_average)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yin, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yin_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(0, 255, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yang, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang_b)))
        self.model.item(self.row_tableview, line_tableview).setForeground(QBrush(QColor(255, 0, 0)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_zero)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_zero)))
        self.row_tableview += 1

    def clearTableView(self):
        self.rowTableView = 0
        # self.model.clear()
        self.tableView.clearSpans()
    def openWaveDisplay(self):
        self.wave = Wave()
        self.isWaveOpen = True
        self.wave.closed.connect(self.OnWaveClosed)

    def OnWaveClosed(self):
        print("wave window closed")
        self.isWaveOpen = False



    def scheduledSend(self):
        self.isScheduledSending = True
        while self.sendSettingsScheduledCheckBox.isChecked():
            self.sendData()
            try:
                time.sleep(int(self.sendSettingsScheduled.text().strip()) / 1000)
            except Exception:
                self.errorSignal.emit(parameters.strTimeFormatError)
        self.isScheduledSending = False

    def MoveToCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def errorHint(self, str):
        QMessageBox.information(self, str, str)

    # def closeEvent(self, event):
    #
    #     reply = QMessageBox.question(self, 'Sure To Quit?',
    #                                  "Are you sure to quit?", QMessageBox.Yes |
    #                                  QMessageBox.No, QMessageBox.No)
    #     if reply == QMessageBox.Yes:
    #         self.com.close()
    #         self.receiveProgressStop = True
    #         self.programExitSaveParameters()
    #         event.accept()
    #     else:
    #         event.ignore()

    def showCombobox(self):
        self.serialPortCombobox.showPopup()




    def programExitSaveParameters(self):
        paramObj = parameters.ParametersToSave()
        paramObj.baudRate = self.serailBaudrateCombobox.currentIndex()
        paramObj.dataBytes = self.serailBytesCombobox.currentIndex()
        paramObj.parity = self.serailParityCombobox.currentIndex()
        paramObj.stopBits = self.serailStopbitsCombobox.currentIndex()
        paramObj.skin = self.param.skin
        if self.receiveSettingsHex.isChecked():
            paramObj.receiveAscii = False
        if not self.receiveSettingsAutoLinefeed.isChecked():
            paramObj.receiveAutoLinefeed = False
        else:
            paramObj.receiveAutoLinefeed = True
        paramObj.receiveAutoLindefeedTime = self.receiveSettingsAutoLinefeedTime.text()
        if self.sendSettingsHex.isChecked():
            paramObj.sendAscii = False
        if not self.sendSettingsScheduledCheckBox.isChecked():
            paramObj.sendScheduled = False
        paramObj.sendScheduledTime = self.sendSettingsScheduled.text()
        if not self.sendSettingsCFLF.isChecked():
            paramObj.useCRLF = False
        paramObj.sendHistoryList.clear()
        for i in range(0, self.sendHistory.count()):
            paramObj.sendHistoryList.append(self.sendHistory.itemText(i))
        if self.checkBoxRts.isChecked():
            paramObj.rts = 1
        else:
            paramObj.rts = 0
        if self.checkBoxDtr.isChecked():
            paramObj.dtr = 1
        else:
            paramObj.dtr = 0
        paramObj.encodingIndex = self.encodingCombobox.currentIndex()
        f = open(parameters.configFilePath, "wb")
        f.truncate()
        pickle.dump(paramObj, f)
        pickle.dump(paramObj.sendHistoryList, f)
        f.close()

    def programStartGetSavedParameters(self):
        paramObj = parameters.ParametersToSave()
        try:
            f = open(parameters.configFilePath, "rb")
            paramObj = pickle.load(f)
            paramObj.sendHistoryList = pickle.load(f)
            f.close()
        except Exception as e:
            f = open(parameters.configFilePath, "wb")
            f.close()
        self.serailBaudrateCombobox.setCurrentIndex(paramObj.baudRate)
        self.encodingCombobox.setCurrentIndex(paramObj.encodingIndex)
        self.param = paramObj





    def functionAdd(self):
        QMessageBox.information(self, "On the way", "On the way")

    def showHideSettings(self):
        if self.isHideSettings:
            self.showSettings()
            self.isHideSettings = False
        else:
            self.hideSettings()
            self.isHideSettings = True

    def showSettings(self):
        self.settingWidget.show()
        self.settings_button.setStyleSheet(
            parameters.strStyleShowHideButtonLeft.replace("$DataPath", self.DataPath))

    def hideSettings(self):
        self.settingWidget.hide()
        self.settings_button.setStyleSheet(
            parameters.strStyleShowHideButtonRight.replace("$DataPath", self.DataPath))

    def showHideFunctional(self):
        if self.isHideFunctinal:
            self.showFunctional()
            self.isHideFunctinal = False
        else:
            self.hideFunctional()
            self.isHideFunctinal = True

    def showFunctional(self):
        self.optional_stock_list_Wiget.show()
        self.functional_button.setStyleSheet(
            parameters.strStyleShowHideButtonRight.replace("$DataPath", self.DataPath))

    def hideFunctional(self):
        self.optional_stock_list_Wiget.hide()
        self.functional_button.setStyleSheet(
            parameters.strStyleShowHideButtonLeft.replace("$DataPath", self.DataPath))

    def skinChange(self):
        if self.param.skin == 1:  # light
            file = open(self.DataPath + '/assets/qss/style-dark.qss', "r")
            self.param.skin = 2
        else:
            file = open(self.DataPath + '/assets/qss/style.qss', "r")
            self.param.skin = 1
        self.app.setStyleSheet(file.read().replace("$DataPath", self.DataPath))

    def showAbout(self):
        QMessageBox.information(self, "About", "<h1 style='color:#f75a5a';margin=10px;>" + parameters.appName +
                                '</h1><br><b style="color:#08c7a1;margin = 5px;">V' + str(
            helpAbout.versionMajor) + "." +
                                str(helpAbout.versionMinor) + "." + str(helpAbout.versionDev) +
                                "</b><br><br>" + helpAbout.date + "<br><br>" + helpAbout.strAbout())



    def clearHistory(self):
        self.param.sendHistoryList.clear()
        self.sendHistory.clear()
        self.errorSignal.emit("History cleared!")

    def autoUpdateDetect(self):
        auto = autoUpdate.AutoUpdate()
        if auto.detectNewVersion():
            auto.OpenBrowser()

    def openDevManagement(self):
        os.system('start devmgmt.msc')

