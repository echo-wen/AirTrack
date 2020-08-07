import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import serial

# 串口Com：读取数据，协议解析，
# Mysql 连接，存入，删除，查询取出数据

class ComFunc():
    def opencom(self):
        try:
            ser = serial.Serial()
            ser.baudrate = 115200  #
            ser.port = 'COM5'
            ser.open()  # 打开串口
            print(ser.port + "串口打开成功")
        except Exception as e:
            print("---异常---：", e)
            ser.close()
        return ser

    # 解析协议：标志："AAAA" + LEN+ 数据+ SUM（校验）
    def analysisprotocol(self, data,log):
        print("s = ", data)
        data_pre = data.hex()
        print("读取到的16进制字符串：", data_pre)
        #### 根据协议解析字符串
        temp = data_pre.find('abcd', 0, len(data_pre))
        print("temp = ", temp)
        LEN = temp + 5  # LEN位
        lendatapre = np.short(int(data_pre[LEN], 16))  # 数据长度
        lendata = lendatapre * 2
        if not (lendata == 12):
            return 0, 0, 0
        print("LEN = ", LEN)  # 打印LEN位置数据
        print("lendata = ", lendata)
        SUM = LEN + lendata + 1  # SUM位
        print("####,", int(data_pre[SUM:SUM + 2], 16))
        sumdata = np.short(int(data_pre[SUM:SUM + 2], 16))
        print("SUM = ", SUM)
        print("sumdata = ", sumdata)
        data_target = data_pre[LEN + 1:LEN + lendata + 1]
        if not (len(data_target) == lendata):
            return 0, 0, 0
        print("data_target = ", data_target)
        XSstr = data_target[0:4]  # 截取第三位到四位的字符
        YSstr = data_target[4:8]
        ZSstr = data_target[8:12]

        XS = np.short(int(XSstr, 16))
        YS = np.short(int(YSstr, 16))
        ZS = np.short(int(ZSstr, 16))
        print("XS = ", XS)
        print("YS = ", YS)
        print("ZS = ", ZS)
        if not (XS + YS + ZS == sumdata):  # 接收正确
            return 0, 0, 0
        log = log + 1  # 传输次数记录+1
        print("log = ", log)
        return XS, YS, ZS


# 数据库
class MysqlFunc():
    def ConnMySql(self):
        global cnn
        config = {'host': '127.0.0.1',  # 默认127.0.0.1
                  'user': 'root',
                  'password': '123456',
                  'port': 3306,  # 默认即为3306
                  'database': 'mysql',
                  'charset': 'utf8'  # 默认即为utf8
                  }
        try:
            cnn = mysql.connector.connect(**config)  # connect方法加载config的配置进行数据库的连接，完成后用一个变量进行接收
        except mysql.connector.Error as e:
            print('数据库链接失败！', str(e))
        return cnn

    # 查询数据库，读取信息到table
    def SelectMySql(self, start, end, cnn):
        try:
            cursor = cnn.cursor(buffered=True)  # 获取查询的标记位
            sql_query2 = 'select * from earthmagnetic where id between {0} and {1}'.format(start, end)
            print(sql_query2)
            cursor.execute(sql_query2)
            table_temp = cursor.fetchmany(10)
        except mysql.connector.Error as e:
            print('查询数据报错！', str(e))
        finally:
            cursor.close()  # 关闭标记位
            cnn.close()  # 关闭数据库链接
        return table_temp

    def SaveMysql(self, log, XS, YS, ZS, cnn_init):
        # cnn_init = self.ConnMySql()
        cursor_init = cnn_init.cursor(buffered=True)  # 获取查询的标记位
        try:
            sql = "insert into earthmagnetic(id,XS,YS,ZS)values('%d','%f','%f','%f')" % (log, XS, YS, ZS)  # 存入数据库
            cursor_init.execute(sql)
            cnn_init.commit()  # 提交到数据库执行，一定要记提交哦
            # print(sql)
        except mysql.connector.Error as e:
            print('查询数据报错！', str(e))
            return



