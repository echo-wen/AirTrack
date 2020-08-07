import _thread
import random

import time
from threading import Lock

import matplotlib
from PyQt5 import QtCore, QtGui, QtWidgets
import hj_func
import hj_ui
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

lock = Lock()
datax = [22,33,44]
datay = [22,33,44]
dataz = [22,33,44]


def updataqueue(XS, YS, ZS):
    lock.acquire()
    if len(datax) > 30:
        for i in range(5):
            del datax[i]
    if len(datay) > 30:
        for j in range(5):
            del datay[j]
    if len(dataz) > 30:
        for k in range(5):
            del dataz[k]
    datax.append(XS)
    datay.append(YS)
    dataz.append(ZS)
    lock.release()
    pass


class ImgDisp(QMainWindow, hj_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ImgDisp, self).__init__(parent)
        self.flag2draw = False
        self.setupUi(self)
        # set Btn
        self.pushButton.clicked.connect(self.BtnInit)
        self.pushButton_2.clicked.connect(self.BtnStart)
        self.pushButton_5.clicked.connect(self.BtnEnd)
        self.pushButton_3.clicked.connect(self.PrintData)
        # set thread
        self.mythread_init = MyThreadInit()  # 实例化线程对象

        # self.mythread_start = MyThreadStart()
        # self.mythread_start.start()  # 启动任务线程
        # self.mythread_start.signal.connect(self.Start_Callback)  # 线程自定义信号连接的槽函数 #设置任务线程发射信号触发的函数

        self.Init_Widgets()

    def Init_Widgets(self):
        self.PrepareSamples()
        self.PrepareSurfaceCanvas()

    # 准备工作
    def PrepareSamples(self):
        self.sql = hj_func.MysqlFunc()
        self.cnn = self.sql.ConnMySql()
        self.timer = QTimer(self)
        print("准备就绪")
        return

    def BtnInit(self):  
        print("Btninit running")
        self.mythread_init.start()  # 启动任务线程

    def BtnStart(self):
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(100)

    def update_figure(self):
        lock.acquire()
        print("update_figure start")
        self.ax3d.clear()
        self.ax3d.plot(datax, datay, dataz, c='r')
        self.SurfFigure.draw()

        print("update_figure end")
        lock.release()

    def PrintData(self):
        print("datax = ", datax)
        print("len(datax) = ", len(datax))
        print("datay = ", datay)
        print("len(datay) = ", len(datay))
        print("dataz = ", dataz)
        print("len(dataz) = ", len(dataz))
        print("\n")

    # 添加画布函数
    def PrepareSurfaceCanvas(self):
        print("PrepareSurfaceCanvas  start")
        # 创建一个合适的画布，通过Figure_canvas()
        self.SurfFigure = Figure_Canvas()
        # 将groupbox这个容器放入gridlaout 网格布局 ，groupBox在hj_ui中通过qtdesigner添加
        self.SurfFigureLayout = QGridLayout(self.groupBox)
        # 画布放入布局中的容器groupBox中
        self.SurfFigureLayout.addWidget(self.SurfFigure)
        self.SurfFigure.ax.remove()
        self.ax3d = self.SurfFigure.fig.gca(projection='3d')
        self.ax3d.set_title("AirTrack")
        self.ax3d.set_xlabel("x")
        self.ax3d.set_ylabel("y")
        self.ax3d.set_zlabel("z")
        print("PrepareSurfaceCanvas end")
        self.figure = self.ax3d.plot(datax, datay, dataz, c='r')
        # plt.show()

    # def ToSaveMysql(self, log, sql):
    #     while True:
    #         print("定时器触发，tosavemysql log = ", self.log)
    #         log = self.log + 1
    #         lock.acquire()
    #         XS = datax.pop(0)
    #         YS = datay.pop(0)
    #         ZS = dataz.pop(0)
    #         lock.release()
    #         sql.SaveMysql(log, XS, YS, ZS, self.cnn)
    #         time.sleep(1.1)

    def BtnEnd(self):
        print("结束！！！")
        self.mythread_init.initflag = False
        self.mythread_init.quit()
        self.mythread_init.wait()
        self.timer.stop()
        pass


class Figure_Canvas(FigureCanvas):
    def __init__(self, parent=None, width=22, height=20, dpi=100):
        self.fig = Figure(figsize=(width, height))
        super(Figure_Canvas, self).__init__(self.fig)
        self.ax = self.fig.add_subplot(111)


# 线程类
class MyThreadInit(QThread):  # 建立一个任务线程类
    # signal = pyqtSignal(int)  # 设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self):
        super(MyThreadInit, self).__init__()
        self.log = 0
        # self.com = hj_func.ComFunc()
        # self.ser = self.com.opencom()
        self.initflag = True

    def run(self):  # 在启动线程后任务从这个函数里面开始执行
        print("Thread_Init running flag = ", self.initflag)
        while True:
            if self.initflag:
                # self.data = self.ser.read(50)
                # XS, YS, ZS = self.com.analysisprotocol(self.data, self.log)
                time.sleep(0.5)
                XS = random.randint(0, 100)
                YS = random.randint(0, 100)
                ZS = random.randint(0, 100)
                updataqueue(XS, YS, ZS)   # 调用数据更新线程
                # self.data = self.ser.read(30)
                # XS, YS, ZS = self.com.analysisprotocol(self.data)
                # print(datax)
    def quit(self):
        self.ser.close()
        return

# start类

# class MyThreadStart(QThread):  # 建立一个任务线程类
#     signal = pyqtSignal(bool)  # 设置触发信号传递的参数数据类型,这里是字符串
#
#     def __init__(self):
#         super(MyThreadStart, self).__init__()
#         self.log = 0
#
#     def run(self):  # 在启动线程后任务从这个函数里面开始执行
