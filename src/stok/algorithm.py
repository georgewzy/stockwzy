


import baostock as bs
import pandas as pd




class Alg(object):
    def __init__(self):
        print("__init__")
        # self.conn = self.connect_database()

    def __del__(self):
        pass


    def get_15m_history_data(self):
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

        lg = bs.login()
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
        stock_code = self.stock_code_lineEdit.text()
        if stock_code[0] == '6':
            stock_code =  'sh.' + stock_code
        else:
            stock_code = 'sz.' + stock_code

        timePeriod = self.time_period_combobox.currentText()

        rd = bs.query_history_k_data_plus(stock_code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=self.start_date_edit.text(), end_date=self.end_date_edit.text(),
                                          frequency="d",
                                          adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权
        print('query_history_k_data_plus respond error_code:' + rd.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rd.error_msg)

        day_list = []
        while (rd.error_code == '0') & rd.next():
            # 获取一条记录，将记录合并在一起
            day_list.append(rd.get_row_data())

        print(day_list)
        shoupanjia = day_list[0][5]

        dateTime_p = datetime.datetime.strptime(day_list[0][0], '%Y-%m-%d').date()
        tomorrow_date = dateTime_p + datetime.timedelta(days=1)
        start_date = str(tomorrow_date)
        end_date = self.end_date_edit.text()


        rs = bs.query_history_k_data_plus(stock_code,
                                          "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                          start_date=start_date, end_date=self.end_date_edit.text(),
                                          frequency='15', adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权


        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
        bs.logout()
        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        print(len(data_list))
        result = pd.DataFrame(data_list, columns=rs.fields)
        print(result)
        result.to_excel('E:/github/stockwzy/datas/002789/00278915.xlsx')

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  # 计算总成交量
            if line_count_yang == 0 and line_count_yin == 0:  #
                pctChg = (float(data_list[i][6]) - float(shoupanjia)) / float(shoupanjia) * 100
            else:
                pctChg = (float(data_list[i][6]) - float(data_list[i - 1][6])) / float(data_list[i - 1][6]) * 100
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
        volume_total = round(volume_total / 100)  # 股数转手（1手=100）
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

    def get_15m_b_history_data(self):
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

        lg = bs.login()
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
        stock_code = self.stock_code_lineEdit.text()
        if stock_code[0] == '6':
            stock_code =  'sh.' + stock_code
        else:
            stock_code = 'sz.' + stock_code

        timePeriod = self.time_period_combobox.currentText()


        rd = bs.query_history_k_data_plus(stock_code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=self.start_date_edit.text(), end_date=self.end_date_edit.text(),
                                          frequency="d",
                                          adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权
        print('query_history_k_data_plus respond error_code:' + rd.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rd.error_msg)

        day_list = []
        while (rd.error_code == '0') & rd.next():
            # 获取一条记录，将记录合并在一起
            day_list.append(rd.get_row_data())

        print(day_list)
        shoupanjia = day_list[0][5]

        dateTime_p = datetime.datetime.strptime(day_list[0][0], '%Y-%m-%d').date()
        tomorrow_date = dateTime_p + datetime.timedelta(days=1)
        start_date = str(tomorrow_date)
        end_date = self.end_date_edit.text()


        rs = bs.query_history_k_data_plus(stock_code,
                                          "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                          start_date=start_date, end_date=self.end_date_edit.text(),
                                          frequency='15', adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权


        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
        bs.logout()
        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        print(len(data_list))
        result = pd.DataFrame(data_list, columns=rs.fields)
        print(result)
        # result.to_excel('E:/github/stockwzy/datas/002789/00278915.xlsx')

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  # 计算总成交量
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
        volume_total = round(volume_total / 100)  # 股数转手（1手=100）
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

    def get_30m_history_data(self):
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

        lg = bs.login()
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)

        stock_code = self.stock_code_lineEdit.text()
        if stock_code[0] == '6':
            stock_code =  'sh.' + stock_code
        else:
            stock_code = 'sz.' + stock_code

        timePeriod = self.time_period_combobox.currentText()

        rd = bs.query_history_k_data_plus(stock_code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=self.start_date_edit.text(),
                                          end_date=self.end_date_edit.text(),
                                          frequency="d",
                                          adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权
        print('query_history_k_data_plus respond error_code:' + rd.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rd.error_msg)

        day_list = []
        while (rd.error_code == '0') & rd.next():
            # 获取一条记录，将记录合并在一起
            day_list.append(rd.get_row_data())

        shoupanjia = day_list[0][5]
        dateTime_p = datetime.datetime.strptime(day_list[0][0], '%Y-%m-%d').date()
        tomorrow_date = dateTime_p + datetime.timedelta(days=1)
        start_date = str(tomorrow_date)
        end_date = self.end_date_edit.text()
        rs = bs.query_history_k_data_plus(stock_code,
                                          "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                          start_date=start_date, end_date=end_date,
                                          frequency='30', adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权

        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
        bs.logout()
        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        print(len(data_list))
        result = pd.DataFrame(data_list, columns=rs.fields)
        print(result)
        # result.to_excel('E:/github/stockwzy/datas/002789/00278930.xlsx')


        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  # 计算总成交量
            if line_count_yang == 0 and line_count_yin == 0:  #
                pctChg = (float(data_list[i][6]) - float(shoupanjia)) / float(shoupanjia) * 100
            else:
                pctChg = (float(data_list[i][6]) - float(data_list[i - 1][6])) / float(data_list[i - 1][6]) * 100
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


    def get_30m_b_history_data(self):
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

        lg = bs.login()
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)

        stock_code = self.stock_code_lineEdit.text()
        if stock_code[0] == '6':
            stock_code =  'sh.' + stock_code
        else:
            stock_code = 'sz.' + stock_code

        timePeriod = self.time_period_combobox.currentText()

        rd = bs.query_history_k_data_plus(stock_code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=self.start_date_edit.text(),
                                          end_date=self.end_date_edit.text(),
                                          frequency="d",
                                          adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权
        print('query_history_k_data_plus respond error_code:' + rd.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rd.error_msg)

        day_list = []
        while (rd.error_code == '0') & rd.next():
            # 获取一条记录，将记录合并在一起
            day_list.append(rd.get_row_data())

        shoupanjia = day_list[0][5]
        dateTime_p = datetime.datetime.strptime(day_list[0][0], '%Y-%m-%d').date()
        tomorrow_date = dateTime_p + datetime.timedelta(days=1)
        start_date = str(tomorrow_date)
        end_date = self.end_date_edit.text()
        rs = bs.query_history_k_data_plus(stock_code,
                                          "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                          start_date=start_date, end_date=end_date,
                                          frequency='30', adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权

        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
        bs.logout()
        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        print(len(data_list))
        result = pd.DataFrame(data_list, columns=rs.fields)
        print(result)
        # result.to_excel('E:/github/stockwzy/datas/002789/00278930.xlsx')

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])  # 计算总成交量
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


    def get_day_history_data1(self):
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
        lg = bs.login()
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)

        stock_code = self.stock_code_lineEdit.text()
        if stock_code[0] == '6':
            stock_code =  'sh.' + stock_code
        else:
            stock_code = 'sz.' + stock_code
        timePeriod = self.time_period_combobox.currentText()

        dateTime_p = datetime.datetime.strptime(self.start_date_edit.text(), '%Y-%m-%d').date()
        tomorrow_date = dateTime_p + datetime.timedelta(days=1)
        start_date = str(tomorrow_date)
        end_date = self.end_date_edit.text()

        if timePeriod == "d":
            rs = bs.query_history_k_data_plus(stock_code,
                                              "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                              start_date=start_date, end_date=end_date,
                                              frequency="d",
                                              adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权
        else:
            rs = bs.query_history_k_data_plus(stock_code,
                                              "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                              start_date=start_date, end_date=end_date, frequency=timePeriod,
                                              adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权

        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
        bs.logout()
        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        print(len(data_list))
        result = pd.DataFrame(data_list, columns=rs.fields)
        print(result)
        result.to_excel('E:/github/stockwzy/datas/002789/002789D.xlsx')

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])
            pctchg_total = pctchg_total + float(data_list[i][12])

            if float(data_list[i][12] == 0):
                volume_zero = volume_zero + int(data_list[i][7])
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


    def get_day_b_history_data(self):
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

        lg = bs.login()
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)

        stock_code = self.stock_code_lineEdit.text()
        if stock_code[0] == '6':
            stock_code =  'sh.' + stock_code
        else:
            stock_code = 'sz.' + stock_code
        timePeriod = self.time_period_combobox.currentText()

        dateTime_p = datetime.datetime.strptime(self.start_date_edit.text(), '%Y-%m-%d').date()
        tomorrow_date = dateTime_p + datetime.timedelta(days=1)
        start_date = str(tomorrow_date)
        end_date = self.end_date_edit.text()


        rs = bs.query_history_k_data_plus(stock_code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=start_date, end_date=end_date,
                                          frequency="d",
                                          adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权


        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
        bs.logout()
        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        print(len(data_list))
        result = pd.DataFrame(data_list, columns=rs.fields)
        print(result)
        # result.to_excel('E:/github/stockwzy/datas/002789/002789D.xlsx')

        for i in range(len(data_list)):
            volume_total = volume_total + int(data_list[i][7])
            pctChg = (float(data_list[i][5]) - float(data_list[i][2])) / float(data_list[i][2]) * 100
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
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(round(pctchg_yang, 2))))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_yang)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(line_count_zero)))
        line_tableview += 1
        self.model.setItem(self.row_tableview, line_tableview, QStandardItem(str(volume_zero)))
        self.row_tableview += 1




