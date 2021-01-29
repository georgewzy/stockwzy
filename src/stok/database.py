
import sqlite3




class SqliteHelper(object):

    def __init__(self):
        print("__init__")
        # self.conn = self.connect_database()

    def __del__(self):
        pass

    def test(self):
        print("vbvvvvvv")

    def create_database(self):
        print("create_database")


    def connect_database(self):
        try:
            conn = sqlite3.connect('E:/github/stockwzy/src/stok/stocks.db')
            print("connect successfully", conn)
        except Exception as e:
            conn = sqlite3.connect('E:/github/stockwzy/src/stok/stocks.db')
            print("SqliteHelper.connectDB:{}".format(e))
        return conn

    def create_stock_table(self, table_name):
        try:
            conn = self.connect_database()
            cur = conn.cursor()
            sql = '''CREATE TABLE {}
                    (
                    stock_code             VARCHAR(10) PRIMARY KEY     NOT NULL,
                    stock_name             VARCHAR(10)            NOT NULL
                    )'''.format(table_name)
            cur.execute(sql)
            conn.commit()
            conn.close()
            print("Table created successfully:{}".format(table_name))
        except Exception as e:
            print("Table created fail:{}".format(table_name))


    def insert_stock(self, table_name, stock_code, stock_name):
        try:
            conn = self.connect_database()
            cur = conn.cursor()
            sql = '''INSERT INTO {} (stock_code, stock_name) VALUES ('{}', '{}')'''.format(table_name, stock_code, stock_name)
            cur.execute(sql)
            conn.commit()
            conn.close()
            print("insertData successfully")
        except Exception as e:
            print("insertData:{}".format(e))

    def select_stock(self, table_name):
        try:
            conn = self.connect_database()
            c = conn.cursor()
            sql = '''SELECT * from {}'''.format(table_name)
            cur = c.execute(sql)
            res = cur.fetchall()
            conn.commit()
            conn.close()
            print("select_stock successfully")
        except Exception as e:
            print("selectData:{}".format(e))
        return res

    def get_all_data_of_stock(self, table_name, start_date, end_date):
        try:
            conn = self.connect_database()
            c = conn.cursor()
            # sql = '''SELECT * from {} where stock_code = 'sz.002789' '''.format(table_name)
            sql = '''SELECT * from {} where stock_date >= '{}' and stock_date <= '{}' '''.format(table_name, start_date, end_date)
            cur = c.execute(sql)
            res = cur.fetchall()
            conn.commit()
            conn.close()
            print("get_all_data_of_stock successfully")
        except Exception as e:
            print("get_all_data_of_stock:{}".format(e))
            res = False
        return res


    def delete_stock(self, table_name, stock_code):
        try:
            conn = self.connect_database()
            c = conn.cursor()
            sql = '''DELETE from {} where stock_code=('{}')'''.format(table_name, stock_code)
            c.execute(sql)
            conn.commit()
            conn.close()
            print("deleteData successfully", stock_code)
        except Exception as e:
            print("deleteData:{}".format(e))



    def create_day_kline_table(self, table_name):
        try:
            conn = self.connect_database()
            cur = conn.cursor()
            sql = '''CREATE TABLE {}
                    (
                    stock_date                  date PRIMARY KEY,                       
                    stock_code                  VARCHAR(10),  
                    open                        float,
                    high                        float,
                    low                         float,
                    close                       float,
                    preclose                    float,
                    volume                      bigint,
                    amount                      bigint,
                    adjustflag                  int,
                    turn                        float,
                    tradestatus                 int,
                    pctChg                      float
                    )'''.format(table_name)
            cur.execute(sql)
            conn.commit()
            conn.close()
            print("Table created successfully:{}".format(table_name))
        except Exception as e:
            print("Table created fail:{}".format(e))

    def insert_day_kline_data(self, table_name, stock_date, stock_code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg):
        try:
            conn = self.connect_database()
            cur = conn.cursor()
            sql = '''INSERT INTO {}
                    (stock_date, stock_code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg) VALUES
                    ( '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
                    )'''.format(table_name, stock_date, stock_code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg)
            cur.execute(sql)
            conn.commit()
            conn.close()
            print("insert_day_kline_data successfully", stock_date, stock_code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg)
        except Exception as e:
            print("insert_day_kline_data:{}".format(e), stock_date, stock_code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg)

    # def select_data(self, table_name):
    #     try:
    #         conn = self.connect_database()
    #         cur = conn.cursor()
    #         sql = '''INSERT INTO {}
    #                        (stock_date, stock_code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg) VALUES
    #                        ( '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
    #                        )'''.format(table_name, stock_date, stock_code, open, high, low, close, preclose, volume,
    #                                    amount, adjustflag, turn, tradestatus, pctChg)
    #         cur.execute(sql)
    #         conn.commit()
    #         conn.close()
    #         conn.close()

    def create_minute_kline_table(self, table_name):
        try:
            conn = self.connect_database()
            cur = conn.cursor()
            sql = '''CREATE TABLE {}
                    (
                    stock_date                  date,
                    stock_time                  text PRIMARY KEY,
                    stock_code                  VARCHAR(10),  
                    open                        float,
                    high                        float,
                    low                         float,
                    close                       float,
                    volume                      bigint,
                    amount                      bigint,
                    adjustflag                  int,
                    pctChg                      float
                    )'''.format(table_name)
            cur.execute(sql)
            conn.commit()
            conn.close()
            print("create_minute_kline_table created successfully:{}".format(table_name))
        except Exception as e:
            print("create_minute_kline_table created fail:{}".format(e))

    def insert_minute_kline_data(self, table_name, stock_date, stock_time, stock_code, open, high, low, close, volume, amount, adjustflag, pctChg):
        try:
            conn = self.connect_database()
            cur = conn.cursor()
            sql = '''INSERT INTO {}
                    (stock_date, stock_time, stock_code, open, high, low, close, volume, amount,adjustflag, pctChg) VALUES
                    ( '{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}
                    )'''.format(table_name, stock_date, stock_time, stock_code, open, high, low, close, volume, amount, adjustflag, pctChg)
            cur.execute(sql)
            conn.commit()
            conn.close()
            print("insert_minute_kline_data successfully", stock_date, stock_time, stock_code, open, high, low, close, volume, amount, adjustflag, pctChg)
        except Exception as e:
            print("insert_minute_kline_data:{}".format(e), stock_date, stock_time, stock_code, open, high, low, close, volume, amount, adjustflag, pctChg)


    def search_table(self, db_file='main.db'):
        conn = self.connect_database()
        cur = conn.cursor()
        cur.execute("select name from sqlite_master where type='table' order by name")
        print(cur.fetchall())


    def delete_table(self, table_name):
        try:
            conn = self.connect_database()
            cur = conn.cursor()
            sql = "drop table {}".format(table_name)
            cur.execute(sql)
            conn.commit()
            conn.close()
            print('delete_table done... table name :{}'.format(table_name))
        except Exception as e:
            print('delete_table done... table name :{}'.format(e))



if __name__ == '__main__':
    sql = SqliteHelper()
    # sql.connect_database()
    # sql.create_stock_table('stock')
    # sql.create_day_kline_table('d002789')
    # sql.create_minute_kline_table('f002789')
    # sql.create_k_day_table('kday_601600')
    # sql.search_table('stocks.db')
    # sql.delete_table('stock')
    # sql.search_table('stocks.db')
    # sql.insert_stock('stock', '5546', 'wzy')
    # sql.insert_day_kline_data('d002789', '2020-1-1', '002789', 17.87,18.08,17.6500000000,17.7100000000,17.8700000000,1547990,27591598.9, 2,	1.797800,1, -0.895400)
    # sql.insert_minute_kline_data('f002789', '2020-11-10', '20201110094500000',	'sz.002789',	17.8700000000,17.8800000000,17.6500000000,17.8500000000,206380,3662634.0000,2)
    # sp = sql.select_stock('d002789')
    # print(sp)
    # sa = sql.get_all_data_of_stock('k002463_d', '2020-01-01', '2020-12-08')
    # if sa == []:
    #     print("vvvvvvvvvv")
    # print(sa)
    sql.delete_stock('stock', "002789")


