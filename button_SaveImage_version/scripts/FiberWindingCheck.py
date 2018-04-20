# -*- coding: utf-8 -*-
# 西安获德图像技术有限公司 -*-
# Code By Charwee 2017/11/21 13:48:21 -*-
#********************************************************************************
'''Less then 80 words'''
#********************************************************************************
import os, sys
import subprocess
import threading
import time
import datetime
import _thread
import socket
import cv2
import numpy as np
import struct
import six
import picamera
import picamera.array
import RPi.GPIO as GPIO
import configparser
import codecs
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.font import Font
from tkinter.ttk import *
from tkinter.messagebox import *

from TftpClient import TftpClient
from SocketClient import SocketClient
from Settings import Settings
from Switch import switch
from GpioOperate import GpioOperate
from TempDatas import TempDatas
#********************************************************************************

# 重写线程操作 线程开启 线程暂停 线程恢复
class ImageProvider(threading.Thread):
    '''图像采集线程'''
    def __init__(self,*args, **kwargs):
        '''asdf'''
        super(ImageProvider, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.set()                   # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()                # 将running设置为True

    def run(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (settings.resolution_width,settings.resolution_height)
            camera.framerate = settings.capturerate
            camera.brightness = settings.brightness
            Frame = np.empty((settings.resolution_height,settings.resolution_width,3),dtype = np.uint8)
            i = 0
            while self.__running.isSet():
                self.__flag.wait()
                # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
                image_size = (settings.resolution_width,settings.resolution_height)
                tempdatas.captured = False
                try:
                    with picamera.array.PiRGBArray(camera,image_size) as stream:
                        try:
                            for frame in camera.capture_continuous(stream, format='bgr', splitter_port = 2, resize = image_size, use_video_port=False):
                                tempdatas.rgbFrame = frame.array #转换到opencv图像
                                tempdatas.grayFrame = cv2.cvtColor(tempdatas.rgbFrame,cv2.COLOR_BGR2GRAY)
                                tempdatas.captured = True
                                i = i+1
                                if i>= 100:
                                    i=0
                                app.frames[StartPage].Label_ErrorTimes['text']='相机心跳： '+ str(i) +' 次'
                                app.frames[StartPage].Label_ErrorTimes.update()
                                stream.seek(0)
                                stream.truncate(0)
                        except Exception as e:
                            camera.close()
                            tempdatas.isDead = True
                            break
                except Exception as e:
                        camera.close()
                        tempdatas.isDead = True
                        break
                finally:
                    time.sleep(0.01)
    #
    def pause(self):
        self.__flag.clear()                 # 设置为False, 让线程阻塞
    #
    def resume(self):
        self.__flag.set()                   # 设置为True, 让线程停止阻塞
    #
    def stop(self):
        self.__flag.set()                   # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()              # 设置为False
#********************************************************************************


#********************************************************************************
# 重写线程操作 线程开启 线程暂停 线程恢复
class ImageProcessor(threading.Thread):
    '''图像处理线程'''
    def __init__(self, *args, **kwargs):
        super(ImageProcessor, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.set()                   # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()                # 将running设置为True
    #
    def run(self):
        while self.__running.isSet():
            self.__flag.wait()              # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            if tempdatas.captured == True:
                tempdatas.captured = False
                tempImage = tempdatas.grayFrame.copy()
                CheckFiberWindingBreak(tempImage)
    #
    def pause(self):
        self.__flag.clear()                 # 设置为False, 让线程阻塞
    #
    def resume(self):
        self.__flag.set()                   # 设置为True, 让线程停止阻塞
    #
    def stop(self):
        self.__flag.set()                   # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()              # 设置为False
#*******************************************************************************


def CheckFiberWindingBreak(inImage):
    '''检测拉丝断头算法'''
    global windingErrorTimes
    hour = datetime.datetime.now().strftime('%H')
    mintue = datetime.datetime.now().strftime('%M')
    hourint = int(hour)
    mintueint = int(mintue)

    for case in switch(tempdatas.condition):
        if case(iStatus_start):
            if tempdatas.startflag == True:
                tempdatas.iStatus = 0#本机状态正常
                # 开始学习
                style = Style()
                style.configure('TCommand_RunFlag.TButton', background='blue',font=('楷体',18,'bold'))
                app.frames[StartPage].Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
                app.frames[StartPage].Command_RunFlag.configure(text='开始学习')
                app.frames[StartPage].Command_RunFlag.update()
                tempdatas.condition = iStatus_learning
                tempdatas.avgValues = [0,0,0,0,0,0]
                tempdatas.index = 0
                break
        if case(iStatus_learning):
            '''学习分块均值'''
            tempdatas.index=tempdatas.index + 1
            #开始学习
            if tempdatas.index >=20:
                tempdatas.avgValues[0] = np.mean(inImage[:,settings.boardPoints_left:settings.boardPoints_left+tempdatas.interval]) + tempdatas.avgValues[0]
                tempdatas.avgValues[1] = np.mean(inImage[:,settings.boardPoints_left+tempdatas.interval:settings.boardPoints_left+2*tempdatas.interval]) + tempdatas.avgValues[1]
                tempdatas.avgValues[2] = np.mean(inImage[:,settings.boardPoints_left+2*tempdatas.interval:settings.boardPoints_left+3*tempdatas.interval]) + tempdatas.avgValues[2]
                tempdatas.avgValues[3] = np.mean(inImage[:,settings.boardPoints_left+3*tempdatas.interval:settings.boardPoints_left+4*tempdatas.interval]) + tempdatas.avgValues[3]
                tempdatas.avgValues[4] = np.mean(inImage[:,settings.boardPoints_left+4*tempdatas.interval:settings.boardPoints_left+5*tempdatas.interval]) + tempdatas.avgValues[4]
                tempdatas.avgValues[5] = np.mean(inImage[:,settings.boardPoints_left+5*tempdatas.interval:settings.boardPoints_left+6*tempdatas.interval]) + tempdatas.avgValues[5]
                style = Style()
                style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
                app.frames[StartPage].Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
                app.frames[StartPage].Command_RunFlag.configure(text='模型建立: ' +str((tempdatas.index-19)/settings.learningIter*100)+'%')
                app.frames[StartPage].Command_RunFlag.update()
                print('start learning '+ str(tempdatas.index))
            if tempdatas.index == 19 + settings.learningIter:
                tempdatas.spiltPerValues[0]=tempdatas.avgValues[0]/settings.learningIter
                tempdatas.spiltPerValues[1]=tempdatas.avgValues[1]/settings.learningIter
                tempdatas.spiltPerValues[2]=tempdatas.avgValues[2]/settings.learningIter
                tempdatas.spiltPerValues[3]=tempdatas.avgValues[3]/settings.learningIter
                tempdatas.spiltPerValues[4]=tempdatas.avgValues[4]/settings.learningIter
                tempdatas.spiltPerValues[5]=tempdatas.avgValues[5]/settings.learningIter
                tempdatas.firstFrame = inImage.copy()# 将最新采集的图像给为前一帧图像
            if tempdatas.index>=20 + settings.learningIter:
                print(tempdatas.spiltPerValues)
                # 学习完毕
                settings.grayAvgValue = tempdatas.spiltPerValues
                settings.SaveParameters()
                app.frames[PageFour].Text35Var.set(settings.grayAvgValue)
                app.frames[PageFour].update()
                settings.LoadParameters()
                app.frames[StartPage].Command_RunFlag.configure(text='建模完毕')
                app.frames[StartPage].Command_RunFlag.update()
                #
                tempdatas.normalNum = 0
                tempdatas.startflag = False
                tempdatas.condition = iStatus_recongnize
                break
            else:
                tempdatas.condition = iStatus_learning
                break
        if case(iStatus_recongnize):
            if tempdatas.machineStart == True:
                style = Style()
                style.configure('TCommand_RunFlag.TButton', background='green',font=('楷体',18,'bold'))
                app.frames[StartPage].Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
                app.frames[StartPage].Command_RunFlag.configure(text='拉丝机已启动...')
                app.frames[StartPage].Command_RunFlag.update()
                time.sleep(20)
                style.configure('TCommand_RunFlag.TButton', background='green',font=('楷体',18,'bold'))
                app.frames[StartPage].Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
                app.frames[StartPage].Command_RunFlag.configure(text='正在检测')
                app.frames[StartPage].Command_RunFlag.update()

                firstFrame = tempdatas.grayFrame.copy()#将最新采集的图像给为前一帧图像
                # 上头成功进入检测状态
                tempdatas.condition = iStatus_normalImage
                tempdatas.machineStart = False
                tempdatas.endShangtou = time.time()
                tempdatas.ShangtouSucessTime = tempdatas.endShangtou
                if tempdatas.startShangtou != 0:
                    tempdatas.timeShangtou = tempdatas.endShangtou - tempdatas.startShangtou - 10
                    ShangtouInfo = dict(strStoveName=settings.stoveName,dateTime=str(datetime.datetime.now()),strShangtouTime=tempdatas.timeShangtou)
                    SendInfo(ShangtouInfo,cmd_ShangtouInfo)
                break
            elif tempdatas.machineStart == False:
                style = Style()
                style.configure('TCommand_RunFlag.TButton', background='yellow',font=('楷体',18,'bold'))
                app.frames[StartPage].Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
                app.frames[StartPage].Command_RunFlag.configure(text='重新引头中')
                app.frames[StartPage].Command_RunFlag.update()
                tempdatas.condition = iStatus_recongnize
                tempdatas.normalNum = 0
                break
            else:
                tempdatas.condition = iStatus_recongnize
                style = Style()
                style.configure('TCommand_RunFlag.TButton', background='yellow',font=('楷体',18,'bold'))
                app.frames[StartPage].Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
                app.frames[StartPage].Command_RunFlag.configure(text='重新引头中')
                app.frames[StartPage].Command_RunFlag.update()
                tempdatas.condition = iStatus_recongnize
                break
        if case(iStatus_normalImage):
            # 判断是否是正常图像
            if caculatePerValues(inImage):
                style = Style()
                style.configure('TFrame_BreakPostion.TLabelframe', background='green',font=('楷体',14,'bold'))
                style.configure('TFrame_BreakPostion.TLabelframe.Label', background='yellow',font=('楷体',14,'bold'))
                app.frames[StartPage].Frame_BreakPostion.configure(style = 'TFrame_BreakPostion.TLabelframe')
                app.frames[StartPage].update()
                detectingAlgorithm(inImage)
                tempdatas.condition = iStatus_checkImage
                break
            else:
                tempdatas.condition = iStatus_normalImage
                print('图像不正常,遮挡或者偏移位置！')
                break
        if case(iStatus_checkImage):
            tempdatas.iStatus = 0
            # 检测算法
            style = Style()
            if tempdatas.errorTimes >= settings.errorTimes:
                tempdatas.iStatus = 1 # 断头状态
                style.configure('TCommand_RunFlag.TButton', background='red',font=('楷体',18,'bold'))
                app.frames[StartPage].Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
                app.frames[StartPage].Command_RunFlag.configure(text='拉丝断头')
                app.frames[StartPage].Command_RunFlag.update()
                # 0 追加到上方 END 追加到最后一行
                app.frames[StartPage].List_Record.insert(0,"断头时间："+time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time())))
                app.frames[StartPage].List_Record.update()
                hour = datetime.datetime.now().strftime('%H')
                mintue = datetime.datetime.now().strftime('%M')
                hourint = int(hour)
                mintueint = int(mintue)
                classType = ''
                if hourint == 20 and mintueint == 0:
                    windingErrorTimes[1] = 0
                if hourint == 8 and mintueint == 0:
                    windingErrorTimes[0] = 0
                if hourint < 20 and hourint >= 8:
                    classType = '白班'
                    p = windingErrorTimes[0]
                    windingErrorTimes[0] = p+1
                else:
                    classType = '晚班'
                    p = windingErrorTimes[1]
                    windingErrorTimes[1] = p+1
                #saveErrorTimes(windingErrorTimes[0],windingErrorTimes[1])
                app.frames[StartPage].Label_Farmes['text']='白班'+str(windingErrorTimes[0])+'次'+' 晚班'+str(windingErrorTimes[1])+'次'

                # group更改背景颜
                style.configure('TFrame_BreakPostion.TLabelframe', background='red',font=('楷体',14,'bold'))
                style.configure('TFrame_BreakPostion.TLabelframe.Label', background='red',font=('楷体',14,'bold'))
                app.frames[StartPage].Frame_BreakPostion.configure(style = 'TFrame_BreakPostion.TLabelframe')

                app.frames[StartPage].lleft.configure(text=str(tempdatas.leftleft))
                app.frames[StartPage].lright.configure(text=str(tempdatas.leftright))
                app.frames[StartPage].midleft.configure(text=str(tempdatas.midleft))
                app.frames[StartPage].midright.configure(text=str(tempdatas.midright))
                app.frames[StartPage].rleft.configure(text=str(tempdatas.rightleft))
                app.frames[StartPage].rright.configure(text=str(tempdatas.rightright))
                app.frames[StartPage].update()
                # 停机处理
                gpio.Machine_Stop()
                # 报警处理
                gpio.ALARME_Start()
                # 延迟两秒翻板
                time.sleep(2)
                # 翻板延迟3秒
                gpio.TurnBoard_Start(settings.turnBoardTimes)
                # 上头时间开始统计
                tempdatas.startShangtou = time.time()
                tempdatas.condition = iStatus_sendInfo
                break
            else:
                tempdatas.condition = iStatus_normalImage
                style.configure('TFrame_BreakPostion.TLabelframe', background='green',font=('楷体',14,'bold'))
                style.configure('TFrame_BreakPostion.TLabelframe.Label', background='green',font=('楷体',14,'bold'))
                app.frames[StartPage].Frame_BreakPostion.configure(style = 'TFrame_BreakPostion.TLabelframe')
                app.frames[StartPage].update()
                break
        if case(iStatus_sendInfo):
            # 记录和显示结果
            try:
                if time.time() - tempdatas.ShangtouSucessTime < 60:
                    ShangtouSucessInfo = dict(strStoveName=settings.stoveName,dateTime=str(datetime.datetime.now()),strSucessType= '0')
                    SendInfo(ShangtouSucessInfo,cmd_ShangtouSucess)
                BrokenInfo = dict(strStoveName=settings.stoveName,dateTime=str(datetime.datetime.now()),strBrokenType=tempdatas.errortype,strBrokenArea=tempdatas.loubanfenbu)
                SendInfo(BrokenInfo,cmd_BrokenInfo)
            finally:
                time.sleep(settings.alarmLightTimes)
                tempdatas.machineStart = False
                gpio.ALARME_Stop()
                gpio.InitGPIOLOW()
                tempdatas.errorTimes = 0
                tempdatas.condition = iStatus_recongnize       
            break
        if case():
            tempdatas.condition = iStatus_recongnize
            break


# 计算和比较图像的灰度均值 四块 0 1 2 3 用一个元组保存
def caculatePerValues(grayFrameTemp):
    avg_1 = 0
    avg_2 = 0
    avg_3 = 0
    avg_4 = 0
    avg_5 = 0
    avg_6 = 0
    interval = tempdatas.interval
    #计算图像的平均灰度
    avg_1 = np.mean(grayFrameTemp[:,settings.boardPoints_left:settings.boardPoints_left+interval]) + avg_1
    avg_2 = np.mean(grayFrameTemp[:,settings.boardPoints_left+interval:settings.boardPoints_left+2*interval]) + avg_2
    avg_3 = np.mean(grayFrameTemp[:,settings.boardPoints_left+2*interval:settings.boardPoints_left+3*interval]) + avg_3
    avg_4 = np.mean(grayFrameTemp[:,settings.boardPoints_left+3*interval:settings.boardPoints_left+4*interval]) + avg_4
    avg_5 = np.mean(grayFrameTemp[:,settings.boardPoints_left+4*interval:settings.boardPoints_left+5*interval]) + avg_5
    avg_6 = np.mean(grayFrameTemp[:,settings.boardPoints_left+5*interval:settings.boardPoints_left+6*interval]) + avg_6
    avgValues = [avg_1,avg_2,avg_3,avg_4,avg_5,avg_6]
    tempdatas.avgValues = avgValues
    print(avgValues)
    isNormal = subListArray(avgValues,tempdatas.spiltPerValues,settings.graythreshold)
    if isNormal:
        return True
    else:
        return False

# 相减的结果，图像是否正常,避免遮挡的影响
def subListArray(array1,array2,threshold):
    ierrorcount = 0
    itruevalues = 0
    for i in range(6):
        subvalues = array1[i]-array2[i]
        if tempdatas.condition == iStatus_recongnize:
            if abs(subvalues) < threshold/4:
                itruevalues = itruevalues + 1
            if abs(subvalues) > threshold:
                ierrorcount = ierrorcount + 1
            else:
                continue
        elif tempdatas.condition == iStatus_normalImage:
            #if abs(subvalues) <= settings.errorValue:
            #    tempdatas.spiltPerValues[i]=(array1[i] + tempdatas.spiltPerValues[i])/2 # 动态学习灰度曲线
            #    continue
            if subvalues < -65:
                ierrorcount = ierrorcount + 1
                app.frames[StartPage].List_Record.insert(0,str(subvalues))
                app.frames[StartPage].List_Record.update()
    #如果五个或者五个以上的区域都趋于标准值来认为是正常的
    #if itruevalues >=5:
    #    tempdatas.normalNum = tempdatas.normalNum + 1
    if ierrorcount>=2:
        return False
    else:
        return True

 
# 检测算法
def detectingAlgorithm(grayFrame):
    try:
        start = time.time()
        if tempdatas.firstFrame is None:
            tempdatas.firstFrame = grayFrame
        image= tempdatas.firstFrame.copy()
        #cv2.imwrite('image.png',image)
        frameDelta = cv2.absdiff(tempdatas.firstFrame,grayFrame)      # 图像的绝对值差
        imageDelta = frameDelta.copy()                               # 拷贝一下，显示有用
        ret,thresh = cv2.threshold(frameDelta,settings.threshold,255,cv2.THRESH_BINARY)# 对差值图像阈值处理
        thresh1 = cv2.dilate(thresh, None, iterations=2)
        (_, cnts, _) = cv2.findContours(thresh1.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        # 异常个数清零
        tempdatas.detectNum = 0
        # 漏板从左到右，六个区域
        tempdatas.leftleft = 0
        tempdatas.leftright = 0
        tempdatas.midleft = 0
        tempdatas.midright = 0
        tempdatas.rightleft = 0
        tempdatas.rightright = 0
        errortype = 2 # 断头类型判断 0 缩头 1 飞头 2 Null
        interval = tempdatas.interval
        for c in cnts:
            if settings.isShowArea == True:
                app.frames[StartPage].List_Record.insert(0,"! 异常："+ str(cv2.contourArea(c)))
                app.frames[StartPage].List_Record.update()
            if cv2.contourArea(c) < settings.areaSet:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            if settings.guasi != "0":
                listguasi = settings.guasi.split(",")
                listguasi.pop()#
                for i in range(int(len(listguasi)/2)):
                    if (x+w)/2 > int(listguasi[i]) and (x+w)/2 <= int(listguasi[i+1]):
                        tempdatas.detectNum = tempdatas.detectNum - 1  
                        break
                    else:
                        continue
            if cv2.contourArea(c) > settings.typeBreakArea and w > 50:
                tempdatas.detectNum = tempdatas.detectNum + 1
                errortype = 1 # 0 缩头 1 飞头
            else:
                if errortype == 1:
                    errortype = 1 # 有飞头则判断为飞头 
                else:
                    errortype = 0 # 没有飞头判断为缩头
                tempdatas.detectNum = tempdatas.detectNum + 1
            # 显示异常区域：颜色加个数

            # lleft lright midleft midright rleft rright
            if (x+w/2)>settings.boardPoints_left and (x+w/2)<=settings.boardPoints_left+interval:
                tempdatas.leftleft = tempdatas.leftleft+1
            elif (x+w/2)>settings.boardPoints_left+interval and (x+w/2)<=settings.boardPoints_left+2*interval:
                tempdatas.leftright = tempdatas.leftright+1
            elif (x+w/2)>settings.boardPoints_left+2*interval and (x+w/2)<=settings.boardPoints_left+3*interval:
                tempdatas.midleft = tempdatas.midleft+1
            elif (x+w/2)>settings.boardPoints_left+3*interval and (x+w/2)<=settings.boardPoints_left+4*interval:
                tempdatas.midright = tempdatas.midright+1
            elif (x+w/2)>settings.boardPoints_left+4*interval and (x+w/2)<=settings.boardPoints_left+5*interval:
                tempdatas.rightleft = tempdatas.rightleft+1
            elif (x+w/2)>settings.boardPoints_left+2*interval and (x+w/2)<=settings.boardPoints_right:
                tempdatas.rightright = tempdatas.rightright+1
            #endfor

        if tempdatas.detectNum == 0:
            tempdatas.errorTimes=0 # 异常次数清零
            gpio.ALARME_Stop()
            app.frames[StartPage].Label_ErrorAreas['text']='异常个数：0 个'
        elif tempdatas.detectNum > 0 and tempdatas.detectNum < settings.errorNumber:
            tempdatas.errorTimes = 0 # 异常次数清零
            app.frames[StartPage].Label_ErrorAreas['text']='异常个数： '+str(tempdatas.detectNum)+' 个'
        elif tempdatas.detectNum >= settings.errorNumber:  
            gpio.ALARME_Start()
            tempdatas.errorTimes= tempdatas.errorTimes + 1
            app.frames[StartPage].Label_ErrorAreas['text']='异常个数： '+str(tempdatas.detectNum)+' 个'
        else:
            tempdatas.errorTimes=0 # 异常次数清零
            app.frames[StartPage].Label_ErrorAreas['text']='异常个数：0 个'
        if tempdatas.errorTimes == 1:
            tempdatas.errortype = errortype # 记录第一次断头漏板区域分布以及飞头类型
            tempdatas.loubanfenbu = [tempdatas.leftleft,tempdatas.leftright,tempdatas.midleft,tempdatas.midright,tempdatas.rightleft,tempdatas.rightright]
        if tempdatas.errorTimes >= 2:
            with open('/home/pi/Desktop/chengwei.txt','a') as my_file:
                strMessage = str(datetime.datetime.now()) +'检测到异常\n'
                my_file.write(strMessage)
            #strdate = str(datetime.datetime.now())
            #path = '/home/pi/Desktop/images/'+strdate+'1.png'
            #cv2.write(path,tempdatas.firstFrame.copy())
            #path = '/home/pi/Desktop/images/'+strdate+'2.png'
            #cv2.write(path,grayFrame.copy())
            
        end = time.time()
        intervaltime = (end-start)
        #print('处理时间'+str(intervaltime))
    finally:
        tempdatas.firstFrame = grayFrame.copy() # 将最新采集的图像给为前一帧图像
        #app.frames[StartPage].Label_ErrorAreas.update()
        app.frames[StartPage].update()


def positionReset():
    '''恢复挂丝设置的button颜色'''
    # lleft lright midleft midright rleft rright
    style = Style()

    style.configure('lleft.TButton',background='green',text='0',font=('楷体',18,'bold'))
    app.frames[StartPage].lleft.configure(style = 'lleft.TButton')
    style.configure('lright.TButton',background='green',text='0',font=('楷体',18,'bold'))
    app.frames[StartPage].lright.configure(style = 'lright.TButton')
    style.configure('midleft.TButton',background='green',text='0',font=('楷体',18,'bold'))
    app.frames[StartPage].midleft.configure(style = 'midleft.TButton')
    style.configure('midright.TButton',background='green',text='0',font=('楷体',18,'bold'))
    app.frames[StartPage].midright.configure(style = 'midright.TButton')
    style.configure('rleft.TButton',background='green',text='0',font=('楷体',18,'bold'))
    app.frames[StartPage].rleft.configure(style = 'rleft.TButton')
    style.configure('rright.TButton',background='green',text='0',font=('楷体',18,'bold'))
    app.frames[StartPage].rright.configure(style = 'rright.TButton')

    app.frames[StartPage].update()


def levelReset():
    style = Style()
    
    style.configure('level1.TButton',background='green',text='1',font=('楷体',18,'bold'))
    app.frames[StartPage].level1.configure(style = 'level1.TButton')
    style.configure('level2.TButton',background='green',text='2',font=('楷体',18,'bold'))
    app.frames[StartPage].level2.configure(style = 'level2.TButton')
    style.configure('level3.TButton',background='green',text='3',font=('楷体',18,'bold'))
    app.frames[StartPage].level3.configure(style = 'level2.TButton')
    style.configure('level4.TButton',background='green',text='4',font=('楷体',18,'bold'))
    app.frames[StartPage].level4.configure(style = 'level4.TButton')
    style.configure('level5.TButton',background='green',text='5',font=('楷体',18,'bold'))
    app.frames[StartPage].level5.configure(style = 'level5.TButton')
    style.configure('level6.TButton',background='green',text='6',font=('楷体',18,'bold'))
    app.frames[StartPage].level6.configure(style = 'level6.TButton')

    app.frames[StartPage].update()







########################################################################
########################################################################




#***********************************************************************
class Application(tk.Tk):
    '''MainFromControl'''
    def __init__(self,master=None):
        super().__init__()
        # 容器
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        # 界面容器
        self.frames = {}
        for F in (StartPage, PageTwo,PageFour):
            frame = F(container, self)
            self.frames[F] = frame
            # 四个页面的位置都是 grid(row=0, column=0), 位置重叠，只有最上面的可见
            frame.grid(row=0, column=0, sticky="nsew")  
        # 显示主界面
        self.show_frame(StartPage)

    '''切换页面显示'''
    def show_frame(self, count):
        frame = self.frames[count]
        frame.tkraise() # 切换，提升当前 tk.Frame z轴顺序（使可见)
#********************************************************************************






#********************************************************************************
def handlerAdaptor(fun, **kwds):
        return lambda event,fun=fun,kwds=kwds: fun(event, **kwds)
#
def Label_Logo_Cmd(event,a):
        a.show_frame(PageTwo)
#
class StartPage(tk.Frame):
    '''主页'''
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.style = Style()
        #self.style.configure('TLabel_Comment.TLabel', anchor='w', font=('楷体',30,'bold'))
        #self.Label_Comment = Label(self, text='拉丝断头检测', style='TLabel_Comment.TLabel')
        #self.Label_Comment.place(relx=0.34, rely=0.033, relwidth=0.401, relheight=0.102)
        self.style.configure('TFrame_CheckParameters.TLabelframe', background='#00FF7F',font=('楷体',14,'bold'))
        self.style.configure('TFrame_CheckParameters.TLabelframe.Label', background='#00FF7F',font=('楷体',14,'bold'))
        self.Frame_CheckParameters = LabelFrame(self, text='低←                                          检测灵敏度                                          →高', style='TFrame_CheckParameters.TLabelframe')
        self.Frame_CheckParameters.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.2)

        #level1
        self.style.configure('level1.TButton',background='green',font=('楷体',16,'bold'))
        self.level1 = Button(self.Frame_CheckParameters, text='1', command=self.level1_cmd, style='level1.TButton')
        self.level1.place(relx=0.01, rely=0.05, relwidth=0.160, relheight=0.85)
        #level2
        self.style.configure('level2.TButton',background='green',font=('楷体',16,'bold'))
        self.level2 = Button(self.Frame_CheckParameters, text='2', command=self.level2_cmd, style='level2.TButton')
        self.level2.place(relx=0.170, rely=0.05, relwidth=0.160, relheight=0.85)
        #level3
        self.style.configure('level3.TButton',background='green',font=('楷体',16,'bold'))
        self.level3 = Button(self.Frame_CheckParameters, text='3', command=self.level3_cmd, style='level3.TButton')
        self.level3.place(relx=0.330, rely=0.05, relwidth=0.160, relheight=0.85)
        #level4
        self.style.configure('level4.TButton',background='green',font=('楷体',16,'bold'))
        self.level4 = Button(self.Frame_CheckParameters, text='4', command=self.level4_cmd, style='level4.TButton')
        self.level4.place(relx=0.510, rely=0.05, relwidth=0.160, relheight=0.85)
        #level5
        self.style.configure('level5.TButton',background='green',font=('楷体',16,'bold'))
        self.level5 = Button(self.Frame_CheckParameters, text='5', command=self.level5_cmd, style='level5.TButton')
        self.level5.place(relx=0.670, rely=0.05, relwidth=0.160, relheight=0.85)
        #level6
        self.style.configure('level6.TButton',background='green',font=('楷体',16,'bold'))
        self.level6 = Button(self.Frame_CheckParameters, text='6', command=self.level6_cmd, style='level6.TButton')
        self.level6.place(relx=0.830, rely=0.05, relwidth=0.160, relheight=0.85)
        #*****************************************************************************
        self.style.configure('TCommand_DebugItem.TButton', font=('楷体',18,'bold'))
        self.Command_DebugItem = Button(self, text='取消挂丝', command=lambda: self.Command_DebugItem_Cmd(root), style='TCommand_DebugItem.TButton')
        self.Command_DebugItem.place(relx=0.59, rely=0.75, relwidth=0.251, relheight=0.235)

        self.style.configure('TCommand_SetParmters.TButton', font=('楷体',18,'bold'))
        self.Command_SetParmters = Button(self, text='参数设置', command=lambda: self.Command_SetParmters_Cmd(root), style='TCommand_SetParmters.TButton')
        self.Command_SetParmters.place(relx=0.38, rely=0.75, relwidth=0.201, relheight=0.235)

        self.style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
        self.Command_RunFlag = Button(self, text='开始检测',command=self.Command_RunFlag_Cmd, style='TCommand_RunFlag.TButton')
        self.Command_RunFlag.place(relx=0.01, rely=0.75, relwidth=0.361, relheight=0.235)
        #*****************************************************************************
        self.style.configure('TFrame_RunDatas.TLabelframe', font=('楷体',14,'bold'))
        self.style.configure('TFrame_RunDatas.TLabelframe.Label', font=('楷体',14,'bold'))
        self.Frame_RunDatas = LabelFrame(self, text='实时运行数据', style='TFrame_RunDatas.TLabelframe')
        self.Frame_RunDatas.place(relx=0.59, rely=0.21, relwidth=0.401, relheight=0.3)

        self.style.configure('TLabel_ErrorTimes.TLabel', anchor='w', font=('楷体',14,'bold'))
        self.Label_ErrorTimes = Label(self.Frame_RunDatas, text='相机心跳：0 次', style='TLabel_ErrorTimes.TLabel')
        self.Label_ErrorTimes.place(relx=0.1, rely=0.35, relwidth=0.601, relheight=0.185)
 
        self.style.configure('TLabel_Farmes.TLabel', anchor='w', font=('楷体',14,'bold'))
        self.Label_Farmes = Label(self.Frame_RunDatas, text='白班：0 次   晚班：0 次', style='TLabel_Farmes.TLabel')
        self.Label_Farmes.place(relx=0.1, rely=0.65, relwidth=0.801, relheight=0.185)

        self.style.configure('TLabel_ErrorAreas.TLabel', anchor='w', font=('楷体',14,'bold'))
        self.Label_ErrorAreas = Label(self.Frame_RunDatas, text='异常个数：0 个', style='TLabel_ErrorAreas.TLabel')
        self.Label_ErrorAreas.place(relx=0.1, rely=0.05, relwidth=0.651, relheight=0.185)
        #*******************************************************************************
        self.style.configure('TFrame_ErrorRecord.TLabelframe', font=('楷体',14,'bold'))
        self.style.configure('TFrame_ErrorRecord.TLabelframe.Label', font=('楷体',14,'bold'))
        self.Frame_ErrorRecord = LabelFrame(self, text='拉丝断头记录', style='TFrame_ErrorRecord.TLabelframe')
        self.Frame_ErrorRecord.place(relx=0.01, rely=0.21, relwidth=0.571, relheight=0.3)

        self.VScroll1 = Scrollbar(self.Frame_ErrorRecord, orient='vertical')
        self.VScroll1.place(relx=0.945, rely=0.059, relwidth=0.037, relheight=0.912)

        global List_RecordVar
        List_RecordVar = StringVar(value=(''))
        self.List_RecordFont = Font(font=('楷体',14,'bold'))
        self.List_Record = Listbox(self.Frame_ErrorRecord, listvariable=List_RecordVar, yscrollcommand=self.VScroll1.set, font=self.List_RecordFont)
        self.List_Record.place(relx=0.018, rely=0.088, relwidth=0.93, relheight=0.85)
        self.VScroll1['command'] = self.List_Record.yview
        #******************************************************************************************
        self.style.configure('TFrame_BreakPostion.TLabelframe', background='#00FF7F',font=('楷体',14,'bold'))
        self.style.configure('TFrame_BreakPostion.TLabelframe.Label', background='#00FF7F',font=('楷体',14,'bold'))
        self.Frame_BreakPostion = LabelFrame(self, text='左←                                           漏板区域                                            →右', style='TFrame_BreakPostion.TLabelframe')
        self.Frame_BreakPostion.place(relx=0.01, rely=0.517, relwidth=0.98, relheight=0.219)
        #lleft
        self.style.configure('lleft.TButton',background='green',font=('楷体',16,'bold'))
        self.lleft = Button(self.Frame_BreakPostion, text='*', command=self.lleft_cmd, style='lleft.TButton')
        self.lleft.place(relx=0.01, rely=0.05, relwidth=0.160, relheight=0.85)
        #lright
        self.style.configure('lright.TButton',background='green',font=('楷体',16,'bold'))
        self.lright = Button(self.Frame_BreakPostion, text='-', command=self.lright_cmd, style='lright.TButton')
        self.lright.place(relx=0.170, rely=0.05, relwidth=0.160, relheight=0.85)
        #midleft
        self.style.configure('midleft.TButton',background='green',font=('楷体',16,'bold'))
        self.midleft = Button(self.Frame_BreakPostion, text='*', command=self.midleft_cmd, style='midleft.TButton')
        self.midleft.place(relx=0.330, rely=0.05, relwidth=0.160, relheight=0.85)
        #midright
        self.style.configure('midright.TButton',background='green',font=('楷体',16,'bold'))
        self.midright = Button(self.Frame_BreakPostion, text='-', command=self.midright_cmd, style='midright.TButton')
        self.midright.place(relx=0.510, rely=0.05, relwidth=0.160, relheight=0.85)
        #rleft
        self.style.configure('rleft.TButton',background='green',font=('楷体',16,'bold'))
        self.rleft = Button(self.Frame_BreakPostion, text='*', command=self.rleft_cmd, style='rleft.TButton')
        self.rleft.place(relx=0.670, rely=0.05, relwidth=0.160, relheight=0.85)
        #rright
        self.style.configure('rright.TButton',background='green',font=('楷体',16,'bold'))
        self.rright = Button(self.Frame_BreakPostion, text='-', command=self.rright_cmd, style='rright.TButton')
        self.rright.place(relx=0.830, rely=0.05, relwidth=0.160, relheight=0.85)
        #******************************************************************************************
        global photologo
        photologo = tk.PhotoImage(file=os.path.dirname(sys.path[0])+ "/images/logo.gif")
        self.style.configure('TLabel_Logo.TLabel', anchor='w', font=('宋体',9))
        self.Label_Logo = Label(self, text='Label5', image=photologo,style='TLabel_Logo.TLabel')
        self.Label_Logo.place(relx=0.85, rely=0.75, relwidth=0.191, relheight=0.235)
        self.Label_Logo.bind("<ButtonPress-1>", handlerAdaptor(Label_Logo_Cmd,a = root))
        
    def Command_DebugItem_Cmd(self,root, event=None):
        '''取消挂丝'''
        try:
            tempdatas.machineStart = True
            settings.guasi = '0'
            positionReset()
            settings.SaveParameters()
            app.frames[PageFour].Text17Var.set(settings.guasi)
            app.frames[PageFour].update()
        except:
            pass

    def Command_SetParmters_Cmd(self,root, event=None):
        '''参数设置'''
        # 暂停检测线程，跳转界面
        if self.Command_RunFlag['text'] == '开始检测':
            root.show_frame(PageFour)
        else:
            root.show_frame(PageFour)
            imageProcessor.pause()
            tempdatas.iStatus = 2
            tempdatas.runflag = False
            style = Style()
            style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
            self.Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
            self.Command_RunFlag.configure(text='暂停检测')
            self.Command_RunFlag.update()
            print ("线程暂停")
        '''time.sleep(0.1)
        global strPwd
        strPwd.clear()
        tempDatas.pageCondition = 1
        root.show_frame(PageThree)
        print ("线程暂停")
        check.pause()
        style = Style()
        style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
        self.Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
        self.Command_RunFlag.configure(text='开始检测')
        self.Command_RunFlag.update()'''

    def Command_RunFlag_Cmd(self, event=None):
        '''开始检测'''
        style = Style()
        if self.Command_RunFlag['text'] == '识别拉丝状态':
            # 重新学习拉丝状态
            tempdatas.startflag = True
            tempdatas.condition = iStatus_start
        elif self.Command_RunFlag['text'] == '暂停检测':
            imageProcessor.resume() # 恢复正在检测
            tempdatas.runflag = True
            style = Style()
            style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
            self.Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
            self.Command_RunFlag.configure(text='正在检测')
            self.Command_RunFlag.update()
        elif self.Command_RunFlag['text'] == '开始检测' and tempdatas.runflag == False:
            imageProvider.start()  # 开始采集
            imageProcessor.start() # 开始检测
            tempdatas.runflag = True
            style = Style()
            style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
            self.Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
            self.Command_RunFlag.configure(text='正在检测')
            self.Command_RunFlag.update()
        elif tempdatas.runflag == False:
            imageProcessor.start()
            style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
            self.Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
            self.Command_RunFlag.configure(text='正在检测')
            self.Command_RunFlag.update()
            tempdatas.runflag = True
        elif tempdatas.runflag == True:
            style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
            self.Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
            self.Command_RunFlag.configure(text='暂停检测')
            imageProcessor.pause() # 暂停检测
            tempdatas.iStatus = 2
            self.Command_RunFlag.update()
            tempdatas.runflag = False
        else:
            pass


    def level1_cmd(self, event=None):
        '''灵敏度——1'''
        settings.threshold = 100
        settings.areaSet = 300
        settings.errorNumber = 3
        settings.errorTimes = 2
        levelReset()
        style = Style()
        style.configure('level1.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level1.configure(style = 'level1.TButton')
        app.frames[StartPage].update()
        settings.SaveParameters()
        app.frames[PageFour].Text11Var.set(settings.threshold)
        app.frames[PageFour].Text12Var.set(settings.areaSet)
        app.frames[PageFour].Text13Var.set(settings.errorNumber)
        app.frames[PageFour].Text14Var.set(settings.errorTimes)
        app.frames[PageFour].update()
    
    def level2_cmd(self, event=None):
        '''灵敏度——2'''
        settings.threshold = 100
        settings.areaSet = 250
        settings.errorNumber = 3
        settings.errorTimes = 2
        levelReset()
        style = Style()
        style.configure('level2.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level2.configure(style = 'level2.TButton')
        app.frames[StartPage].update()
        settings.SaveParameters()
        app.frames[PageFour].Text11Var.set(settings.threshold)
        app.frames[PageFour].Text12Var.set(settings.areaSet)
        app.frames[PageFour].Text13Var.set(settings.errorNumber)
        app.frames[PageFour].Text14Var.set(settings.errorTimes)
        app.frames[PageFour].update()
    
    def level3_cmd(self, event=None):
        '''灵敏度——3'''
        settings.threshold = 95
        settings.areaSet = 300
        settings.errorNumber = 3
        settings.errorTimes = 2
        levelReset()
        style = Style()
        style.configure('level3.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level3.configure(style = 'level3.TButton')
        app.frames[StartPage].update()
        settings.SaveParameters()
        app.frames[PageFour].Text11Var.set(settings.threshold)
        app.frames[PageFour].Text12Var.set(settings.areaSet)
        app.frames[PageFour].Text13Var.set(settings.errorNumber)
        app.frames[PageFour].Text14Var.set(settings.errorTimes)
        app.frames[PageFour].update()
    
    def level4_cmd(self, event=None):
        '''灵敏度——4'''
        settings.threshold = 95
        settings.areaSet = 250
        settings.errorNumber = 3
        settings.errorTimes = 2
        levelReset()
        style = Style()
        style.configure('level4.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level4.configure(style = 'level4.TButton')
        app.frames[StartPage].update()
        settings.SaveParameters()
        app.frames[PageFour].Text11Var.set(settings.threshold)
        app.frames[PageFour].Text12Var.set(settings.areaSet)
        app.frames[PageFour].Text13Var.set(settings.errorNumber)
        app.frames[PageFour].Text14Var.set(settings.errorTimes)
        app.frames[PageFour].update()
    
    def level5_cmd(self, event=None):
        '''灵敏度——5'''
        settings.threshold = 90
        settings.areaSet = 250
        settings.errorNumber = 3
        settings.errorTimes = 2
        levelReset()
        style = Style()
        style.configure('level5.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level5.configure(style = 'level5.TButton')
        app.frames[StartPage].update()
        settings.SaveParameters()
        app.frames[PageFour].Text11Var.set(settings.threshold)
        app.frames[PageFour].Text12Var.set(settings.areaSet)
        app.frames[PageFour].Text13Var.set(settings.errorNumber)
        app.frames[PageFour].Text14Var.set(settings.errorTimes)
        app.frames[PageFour].update()

    def level6_cmd(self, event=None):
        '''灵敏度——6'''
        settings.threshold = 90
        settings.areaSet = 200
        settings.errorNumber = 3
        settings.errorTimes = 2
        levelReset()
        style = Style()
        style.configure('level6.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level6.configure(style = 'level6.TButton')
        app.frames[StartPage].update()
        settings.SaveParameters()
        app.frames[PageFour].Text11Var.set(settings.threshold)
        app.frames[PageFour].Text12Var.set(settings.areaSet)
        app.frames[PageFour].Text13Var.set(settings.errorNumber)
        app.frames[PageFour].Text14Var.set(settings.errorTimes)
        app.frames[PageFour].update()


    def lleft_cmd(self, event=None):
        '''区域最左按钮事件'''
        if settings.guasi == '0':
            settings.guasi = ''
        settings.guasi = settings.guasi + str(settings.boardPoints_left) + ',' + str(settings.boardPoints_left+tempdatas.interval)+','
        style = Style()
        style.configure('lleft.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].lleft.configure(style = 'lleft.TButton')
        app.frames[StartPage].update()

        settings.SaveParameters()
        app.frames[PageFour].Text17Var.set(settings.guasi)
        app.frames[PageFour].update()

    def lright_cmd(self,event=None):
        ''''''
        if settings.guasi == '0':
            settings.guasi = ''
        else:
            settings.guasi = settings.guasi + str(settings.boardPoints_left+tempdatas.interval) + ',' + str(settings.boardPoints_left+2*tempdatas.interval)+','
            style = Style()
            style.configure('lright.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
            app.frames[StartPage].lright.configure(style = 'lright.TButton')
            app.frames[StartPage].update()

            settings.SaveParameters()
            app.frames[PageFour].Text17Var.set(settings.guasi)
            app.frames[PageFour].update()
    
    def midleft_cmd(self,event=None):
        if settings.guasi == '0':
            settings.guasi = ''
        else:
            settings.guasi = settings.guasi + str(settings.boardPoints_left+2*tempdatas.interval) + ',' + str(settings.boardPoints_left+3*tempdatas.interval)+','
            style = Style()
            style.configure('midleft.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
            app.frames[StartPage].midleft.configure(style = 'midleft.TButton')
            app.frames[StartPage].update()

            settings.SaveParameters()
            app.frames[PageFour].Text17Var.set(settings.guasi)
            app.frames[PageFour].update()
    
    def midright_cmd(self, event=None):
        '''区域最右按钮事件'''   
        if settings.guasi == '0':
            settings.guasi = ''
        else:
            settings.guasi = settings.guasi + str(settings.boardPoints_left + 3*tempdatas.interval) + ',' + str(settings.boardPoints_left + 4*tempdatas.interval)+','
            style = Style()
            style.configure('midright.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
            app.frames[StartPage].midright.configure(style = 'midright.TButton')
            app.frames[StartPage].update()

            settings.SaveParameters()
            app.frames[PageFour].Text17Var.set(settings.guasi)
            app.frames[PageFour].update()

    def rleft_cmd(self, event=None):
        '''区域右中按钮事件'''
        if settings.guasi == '0':
            settings.guasi = ''
        else:
            settings.guasi = settings.guasi + str(settings.boardPoints_left + 4*tempdatas.interval) + ',' + str(settings.boardPoints_left + 5*tempdatas.interval)+','
            style = Style()
            style.configure('rleft.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
            app.frames[StartPage].rleft.configure(style = 'rleft.TButton')
            app.frames[StartPage].update()

            settings.SaveParameters()
            app.frames[PageFour].Text17Var.set(settings.guasi)
            app.frames[PageFour].update()

    def rright_cmd(self, event=None):
        '''区域左中按钮事件'''
        if settings.guasi == '0':
            settings.guasi = ''
        else:
            settings.guasi = settings.guasi + str(settings.boardPoints_left + 5*tempdatas.interval) + ',' + str(settings.boardPoints_right)+','
            style = Style()
            style.configure('rright.TButton',background='#1E90FF',text='0',font=('楷体',18,'bold'))
            app.frames[StartPage].rright.configure(style = 'rright.TButton')
            app.frames[StartPage].update()

            settings.SaveParameters()
            app.frames[PageFour].Text17Var.set(settings.guasi)
            app.frames[PageFour].update()
#********************************************************************************



#********************************************************************************
class PageTwo(tk.Frame):
    # 这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, parent, root):
        super().__init__(parent)
        self.createWidgets(root)

    def createWidgets(self,root):
        self.style = Style()
        global photo
        photo = PhotoImage(file=os.path.dirname(sys.path[0])+ "/images/版本界面.gif")
        self.style.configure('TLabel1.TLabel', anchor='w', font=('楷体',14,'bold'))
        self.Label1 = Label(self, text='', image=photo,style='TLabel1.TLabel')
        self.Label1.place(relx=0., rely=0., relwidth=1.001, relheight=0.719)
        self.Label1.bind("<ButtonPress-1>", self.Command_BackMain_Cmd(root))

        self.style.configure('TCommand_BackMain.TButton', background='#00FFFF',font=('楷体',14,'bold'))
        self.Command_BackMain = Button(self, text='返回主界面', command=lambda: self.Command_BackMain_Cmd(root), style='TCommand_BackMain.TButton')
        self.Command_BackMain.place(relx=0., rely=0.75, relwidth=0.991, relheight=0.235)

    def Command_BackMain_Cmd(self, root, event=None):
        #TODO, Please finish the function here!
        root.show_frame(StartPage)
#********************************************************************************



#********************************************************************************
class PageFour(tk.Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, parent, root):
        super().__init__(parent)
        self.createWidgets(root)

    def createWidgets(self,root):
        self.style = Style()
        self.root = root
        self.style.configure('TCommand4.TButton', font=('楷体',18,'bold'))
        self.Command4 = Button(self, text='返回主界面', command=self.Command4_Cmd, style='TCommand4.TButton')
        self.Command4.place(relx=0.75, rely=0.8, relwidth=0.231, relheight=0.185)

        self.style.configure('TCommand3.TButton', font=('楷体',18,'bold'))
        self.Command3 = Button(self, text='保存参数', command=self.Command3_Cmd, style='TCommand3.TButton')
        self.Command3.place(relx=0.5, rely=0.8, relwidth=0.231, relheight=0.185)

        self.style.configure('TCommand2.TButton', font=('楷体',18,'bold'))
        self.Command2 = Button(self, text='恢复默认', command=self.Command2_Cmd, style='TCommand2.TButton')
        self.Command2.place(relx=0.25, rely=0.8, relwidth=0.231, relheight=0.185)

        self.style.configure('TCommand1.TButton', font=('楷体',18,'bold'))
        self.Command1 = Button(self, text='调试图像', command=self.Command1_Cmd, style='TCommand1.TButton')
        self.Command1.place(relx=0.01, rely=0.8, relwidth=0.231, relheight=0.185)

        self.style.configure('TFrame6.TLabelframe', font=('宋体',9))
        self.style.configure('TFrame6.TLabelframe.Label', font=('宋体',9))
        self.Frame6 = LabelFrame(self, text='炉位参数', style='TFrame6.TLabelframe')
        self.Frame6.place(relx=0.01, rely=0.4, relwidth=0.531, relheight=0.369)

        self.style.configure('TFrame3.TLabelframe', font=('宋体',9))
        self.style.configure('TFrame3.TLabelframe.Label', font=('宋体',9))
        self.Frame3 = LabelFrame(self, text='检测参数', style='TFrame3.TLabelframe')
        self.Frame3.place(relx=0.55, rely=0.017, relwidth=0.441, relheight=0.752)

        self.style.configure('TFrame2.TLabelframe', font=('宋体',9))
        self.style.configure('TFrame2.TLabelframe.Label', font=('宋体',9))
        self.Frame2 = LabelFrame(self, text='模型参数', style='TFrame2.TLabelframe')
        self.Frame2.place(relx=0.28, rely=0.017, relwidth=0.261, relheight=0.369)

        self.style.configure('TFrame1.TLabelframe', font=('宋体',9))
        self.style.configure('TFrame1.TLabelframe.Label', font=('宋体',9))
        self.Frame1 = LabelFrame(self, text='相机参数', style='TFrame1.TLabelframe')
        self.Frame1.place(relx=0.01, rely=0.017, relwidth=0.261, relheight=0.369)
        # 服务器端口号
        self.Text30Var = StringVar(value=settings.serverPort)
        self.Text30 = Entry(self.Frame6, textvariable=self.Text30Var, font=('宋体',9))
        self.Text30.place(relx=0.207, rely=0.678, relwidth=0.228, relheight=0.102)
        # 服务器IP
        self.Text29Var = StringVar(value=settings.serverIPaddr)
        self.Text29 = Entry(self.Frame6, textvariable=self.Text29Var, font=('宋体',9))
        self.Text29.place(relx=0.207, rely=0.542, relwidth=0.228, relheight=0.102)
        # 本机端口号
        self.Text28Var = StringVar(value=settings.nativePort)
        self.Text28 = Entry(self.Frame6, textvariable=self.Text28Var, font=('宋体',9))
        self.Text28.place(relx=0.207, rely=0.407, relwidth=0.228, relheight=0.102)
        # 本机IP地址
        self.Text27Var = StringVar(value=settings.nativeIPaddr)
        self.Text27 = Entry(self.Frame6, textvariable=self.Text27Var, font=('宋体',9))
        self.Text27.place(relx=0.207, rely=0.271, relwidth=0.228, relheight=0.102)
        # 本机炉位名称
        self.Text26Var = StringVar(value=settings.stoveName)
        self.Text26 = Entry(self.Frame6, textvariable=self.Text26Var, font=('宋体',9))
        self.Text26.place(relx=0.207, rely=0.136, relwidth=0.228, relheight=0.102)

        self.style.configure('TLabel37.TLabel', anchor='w', font=('宋体',9))
        self.Label37 = Label(self.Frame6, text='晚班断头', style='TLabel37.TLabel')
        self.Label37.place(relx=0.452, rely=0.271, relwidth=0.153, relheight=0.102)

        self.style.configure('TLabel36.TLabel', anchor='w', font=('宋体',9))
        self.Label36 = Label(self.Frame6, text='白班断头', style='TLabel36.TLabel')
        self.Label36.place(relx=0.452, rely=0.136, relwidth=0.153, relheight=0.102)

        self.style.configure('TLabel31.TLabel', anchor='w', font=('宋体',9))
        self.Label31 = Label(self.Frame6, text='本机密码', style='TLabel31.TLabel')
        self.Label31.place(relx=0.038, rely=0.814, relwidth=0.153, relheight=0.102)

        self.style.configure('TLabel30.TLabel', anchor='w', font=('宋体',9))
        self.Label30 = Label(self.Frame6, text='服务器端口', style='TLabel30.TLabel')
        self.Label30.place(relx=0.038, rely=0.678, relwidth=0.153, relheight=0.102)

        self.style.configure('TLabel29.TLabel', anchor='w', font=('宋体',9))
        self.Label29 = Label(self.Frame6, text='服务器IP', style='TLabel29.TLabel')
        self.Label29.place(relx=0.038, rely=0.542, relwidth=0.153, relheight=0.102)

        self.style.configure('TLabel28.TLabel', anchor='w', font=('宋体',9))
        self.Label28 = Label(self.Frame6, text='本机端口号', style='TLabel28.TLabel')
        self.Label28.place(relx=0.038, rely=0.407, relwidth=0.153, relheight=0.102)

        self.style.configure('TLabel27.TLabel', anchor='w', font=('宋体',9))
        self.Label27 = Label(self.Frame6, text='本机IP地址', style='TLabel27.TLabel')
        self.Label27.place(relx=0.038, rely=0.271, relwidth=0.153, relheight=0.102)

        self.style.configure('TLabel26.TLabel', anchor='w', font=('宋体',9))
        self.Label26 = Label(self.Frame6, text='炉位名称', style='TLabel26.TLabel')
        self.Label26.place(relx=0.038, rely=0.136, relwidth=0.153, relheight=0.102)
        # 晚班断头次数
        self.Text37Var = StringVar(value=settings.nightBrokenNum)
        self.Text37 = Entry(self.Frame6, textvariable=self.Text37Var, font=('宋体',9))
        self.Text37.place(relx=0.621, rely=0.271, relwidth=0.228, relheight=0.102)
        # 挂丝设定
        self.Text17Var = StringVar(value=settings.guasi)
        self.Text17 = Entry(self.Frame3, textvariable=self.Text17Var, font=('宋体',9))
        self.Text17.place(relx=0.295, rely=0.465, relwidth=0.637, relheight=0.05)
        # 偏差修正值
        self.Text35Var = StringVar(value=settings.grayAvgValue)
        self.Text35 = Entry(self.Frame3, textvariable=self.Text35Var, font=('宋体',9))
        self.Text35.place(relx=0.295, rely=0.399, relwidth=0.637, relheight=0.05)
        # 翻板时间
        self.Text34Var = StringVar(value=settings.turnBoardTimes)
        self.Text34 = Entry(self.Frame3, textvariable=self.Text34Var, font=('宋体',9))
        self.Text34.place(relx=0.725, rely=0.199, relwidth=0.207, relheight=0.05)
        # 报警时长
        self.Text33Var = StringVar(value=settings.alarmLightTimes)
        self.Text33 = Entry(self.Frame3, textvariable=self.Text33Var, font=('宋体',9))
        self.Text33.place(relx=0.725, rely=0.133, relwidth=0.207, relheight=0.05)
        # 检测等待时间
        self.Text32Var = StringVar(value=settings.waitTime)
        self.Text32 = Entry(self.Frame3, textvariable=self.Text32Var, font=('宋体',9))
        self.Text32.place(relx=0.725, rely=0.066, relwidth=0.207, relheight=0.05)
        # 面积显示  
        self.Text16Var = StringVar(value=settings.isShowArea)
        self.Text16 = Entry(self.Frame3, textvariable=self.Text16Var, font=('宋体',9))
        self.Text16.place(relx=0.725, rely=0.266, relwidth=0.207, relheight=0.05)
        #断头类型判断
        self.Text15Var = StringVar(value=settings.typeBreakArea)
        self.Text15 = Entry(self.Frame3, textvariable=self.Text15Var, font=('宋体',9))
        self.Text15.place(relx=0.295, rely=0.332, relwidth=0.207, relheight=0.05)
        # 异常次数
        self.Text14Var = StringVar(value=settings.errorTimes)
        self.Text14 = Entry(self.Frame3, textvariable=self.Text14Var, font=('宋体',9))
        self.Text14.place(relx=0.295, rely=0.266, relwidth=0.207, relheight=0.05)
        # 异常个数
        self.Text13Var = StringVar(value=settings.errorNumber)
        self.Text13 = Entry(self.Frame3, textvariable=self.Text13Var, font=('宋体',9))
        self.Text13.place(relx=0.295, rely=0.199, relwidth=0.207, relheight=0.05)
        # 面积阈值
        self.Text12Var = StringVar(value=settings.areaSet)
        self.Text12 = Entry(self.Frame3, textvariable=self.Text12Var, font=('宋体',9))
        self.Text12.place(relx=0.295, rely=0.133, relwidth=0.207, relheight=0.05)
        # 检测灰度阈值
        self.Text11Var = StringVar(value=settings.threshold)
        self.Text11 = Entry(self.Frame3, textvariable=self.Text11Var, font=('宋体',9))
        self.Text11.place(relx=0.295, rely=0.066, relwidth=0.207, relheight=0.05)
        # 挂丝设定值
        self.style.configure('TLabel17.TLabel', anchor='w', font=('宋体',9))
        self.Label17 = Label(self.Frame3, text='挂丝设定', style='TLabel17.TLabel')
        self.Label17.place(relx=0.091, rely=0.465, relwidth=0.184, relheight=0.05)
        self.Label17.bind('<Button-1>', self.Label17_Button_1)
        # 区域偏差设定
        self.style.configure('TLabel35.TLabel', anchor='w', font=('宋体',9))
        self.Label35 = Label(self.Frame3, text='偏差修正', style='TLabel35.TLabel')
        self.Label35.place(relx=0.091, rely=0.399, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel34.TLabel', anchor='w', font=('宋体',9))
        self.Label34 = Label(self.Frame3, text='翻板时间', style='TLabel34.TLabel')
        self.Label34.place(relx=0.521, rely=0.199, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel33.TLabel', anchor='w', font=('宋体',9))
        self.Label33 = Label(self.Frame3, text='报警时长', style='TLabel33.TLabel')
        self.Label33.place(relx=0.521, rely=0.133, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel32.TLabel', anchor='w', font=('宋体',9))
        self.Label32 = Label(self.Frame3, text='检测等待', style='TLabel32.TLabel')
        self.Label32.place(relx=0.521, rely=0.066, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel16.TLabel', anchor='w', font=('宋体',9))
        self.Label16 = Label(self.Frame3, text='面积显示', style='TLabel16.TLabel')
        self.Label16.place(relx=0.521, rely=0.266, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel15.TLabel', anchor='w', font=('宋体',9))
        self.Label15 = Label(self.Frame3, text='断头判断', style='TLabel15.TLabel')
        self.Label15.place(relx=0.091, rely=0.332, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel14.TLabel', anchor='w', font=('宋体',9))
        self.Label14 = Label(self.Frame3, text='异常次数', style='TLabel14.TLabel')
        self.Label14.place(relx=0.091, rely=0.266, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel13.TLabel', anchor='w', font=('宋体',9))
        self.Label13 = Label(self.Frame3, text='异常个数', style='TLabel13.TLabel')
        self.Label13.place(relx=0.091, rely=0.199, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel12.TLabel', anchor='w', font=('宋体',9))
        self.Label12 = Label(self.Frame3, text='面积阈值', style='TLabel12.TLabel')
        self.Label12.place(relx=0.091, rely=0.133, relwidth=0.184, relheight=0.05)

        self.style.configure('TLabel11.TLabel', anchor='w', font=('宋体',9))
        self.Label11 = Label(self.Frame3, text='灰度阈值', style='TLabel11.TLabel')
        self.Label11.place(relx=0.091, rely=0.066, relwidth=0.184, relheight=0.05)
        #白班断头次数
        self.Text36Var = StringVar(value=settings.dayBrokenNum)
        self.Text36 = Entry(self.Frame6, textvariable=self.Text36Var, font=('宋体',9))
        self.Text36.place(relx=0.621, rely=0.136, relwidth=0.228, relheight=0.102)
        #识别迭代次数
        self.Text10Var = StringVar(value=settings.reconIter)
        self.Text10 = Entry(self.Frame2, textvariable=self.Text10Var, font=('宋体',9))
        self.Text10.place(relx=0.498, rely=0.814, relwidth=0.349, relheight=0.102)
        #模型迭代学习次数
        self.Text9Var = StringVar(value=settings.learningIter)
        self.Text9 = Entry(self.Frame2, textvariable=self.Text9Var, font=('宋体',9))
        self.Text9.place(relx=0.498, rely=0.678, relwidth=0.349, relheight=0.102)
        #偏差系数   
        self.Text8Var = StringVar(value=settings.errorValue)
        self.Text8 = Entry(self.Frame2, textvariable=self.Text8Var, font=('宋体',9))
        self.Text8.place(relx=0.498, rely=0.542, relwidth=0.349, relheight=0.102)
        #识别阈值
        self.Text7Var = StringVar(value=settings.graythreshold)
        self.Text7 = Entry(self.Frame2, textvariable=self.Text7Var, font=('宋体',9))
        self.Text7.place(relx=0.498, rely=0.407, relwidth=0.349, relheight=0.102)
        #漏板最右端点
        self.Text6Var = StringVar(value=settings.boardPoints_right)
        self.Text6 = Entry(self.Frame2, textvariable=self.Text6Var, font=('宋体',9))
        self.Text6.place(relx=0.498, rely=0.271, relwidth=0.349, relheight=0.102)
        #漏板最左端点
        self.Text5Var = StringVar(value=settings.boardPoints_left)
        self.Text5 = Entry(self.Frame2, textvariable=self.Text5Var, font=('宋体',9))
        self.Text5.place(relx=0.498, rely=0.136, relwidth=0.349, relheight=0.102)

        self.style.configure('TLabel10.TLabel', anchor='w', font=('宋体',9))
        self.Label10 = Label(self.Frame2, text='识别迭代次数', style='TLabel10.TLabel')
        self.Label10.place(relx=0.077, rely=0.814, relwidth=0.388, relheight=0.102)

        self.style.configure('TLabel9.TLabel', anchor='w', font=('宋体',9))
        self.Label9 = Label(self.Frame2, text='模型迭代次数', style='TLabel9.TLabel')
        self.Label9.place(relx=0.077, rely=0.678, relwidth=0.388, relheight=0.102)

        self.style.configure('TLabel8.TLabel', anchor='w', font=('宋体',9))
        self.Label8 = Label(self.Frame2, text='偏差系数', style='TLabel8.TLabel')
        self.Label8.place(relx=0.077, rely=0.542, relwidth=0.388, relheight=0.102)

        self.style.configure('TLabel7.TLabel', anchor='w', font=('宋体',9))
        self.Label7 = Label(self.Frame2, text='识别阈值', style='TLabel7.TLabel')
        self.Label7.place(relx=0.077, rely=0.407, relwidth=0.388, relheight=0.102)

        self.style.configure('TLabel6.TLabel', anchor='w', font=('宋体',9))
        self.Label6 = Label(self.Frame2, text='漏板最右端点', style='TLabel6.TLabel')
        self.Label6.place(relx=0.077, rely=0.271, relwidth=0.388, relheight=0.102)

        self.style.configure('TLabel5.TLabel', anchor='w', font=('宋体',9))
        self.Label5 = Label(self.Frame2, text='漏板最左端点', style='TLabel5.TLabel')
        self.Label5.place(relx=0.077, rely=0.136, relwidth=0.388, relheight=0.102)
        # 本机密码
        self.Text31Var = StringVar(value=settings.password)
        self.Text31 = Entry(self.Frame6, textvariable=self.Text31Var, font=('宋体',9))
        self.Text31.place(relx=0.207, rely=0.814, relwidth=0.228, relheight=0.102)
        # 图像预览
        self.Text22Var = StringVar(value=settings.isPreview)
        self.Text22 = Entry(self.Frame1, textvariable=self.Text22Var, font=('宋体',9))
        self.Text22.place(relx=0.459, rely=0.723, relwidth=0.349, relheight=0.102)
        self.Text22Var.trace('w', self.Text22_Change)
        # 曝光时间
        self.Text4Var = StringVar(value=settings.brightness)
        self.Text4 = Entry(self.Frame1, textvariable=self.Text4Var, font=('宋体',9))
        self.Text4.place(relx=0.459, rely=0.587, relwidth=0.349, relheight=0.102)
        # 采样帧速率
        self.Text3Var = StringVar(value=settings.capturerate)
        self.Text3 = Entry(self.Frame1, textvariable=self.Text3Var, font=('宋体',9))
        self.Text3.place(relx=0.459, rely=0.452, relwidth=0.349, relheight=0.102)
        # 图像宽度
        self.Text2Var = StringVar(value=settings.resolution_width)
        self.Text2 = Entry(self.Frame1, textvariable=self.Text2Var, font=('宋体',9))
        self.Text2.place(relx=0.459, rely=0.271, relwidth=0.349, relheight=0.102)
        # 图像高度
        self.Text1Var = StringVar(value=settings.resolution_height)
        self.Text1 = Entry(self.Frame1, textvariable=self.Text1Var, font=('宋体',9))
        self.Text1.place(relx=0.459, rely=0.136, relwidth=0.349, relheight=0.102)

        self.style.configure('TLabel22.TLabel', anchor='w', font=('宋体',9))
        self.Label22 = Label(self.Frame1, text='图像预览', style='TLabel22.TLabel')
        self.Label22.place(relx=0.115, rely=0.723, relwidth=0.273, relheight=0.102)

        self.style.configure('TLabel4.TLabel', anchor='w', font=('宋体',9))
        self.Label4 = Label(self.Frame1, text='曝光时间', style='TLabel4.TLabel')
        self.Label4.place(relx=0.115, rely=0.588, relwidth=0.273, relheight=0.102)

        self.style.configure('TLabel3.TLabel', anchor='w', font=('宋体',9))
        self.Label3 = Label(self.Frame1, text='采样帧频', style='TLabel3.TLabel')
        self.Label3.place(relx=0.115, rely=0.452, relwidth=0.311, relheight=0.102)

        self.style.configure('TLabel2.TLabel', anchor='w', font=('宋体',9))
        self.Label2 = Label(self.Frame1, text='分辨率_宽', style='TLabel2.TLabel')
        self.Label2.place(relx=0.115, rely=0.271, relwidth=0.311, relheight=0.102)

        self.style.configure('TLabel1.TLabel', anchor='w', font=('宋体',9))
        self.Label1 = Label(self.Frame1, text='分辨率_高', style='TLabel1.TLabel')
        self.Label1.place(relx=0.115, rely=0.136, relwidth=0.311, relheight=0.102)

    def Command4_Cmd(self, event=None):
        '''返回主界面'''
        self.root.show_frame(StartPage)
        pass
    
    def Command3_Cmd(self, event=None):
        '''保存参数'''
        try:
            settings.resolution_width = int(self.Text2.get()) # 相机图像分辨率_宽
            settings.resolution_height = int(self.Text1.get()) # 相机图像分辨率_高
            settings.brightness = int(self.Text4.get()) # 曝光时间
            settings.capturerate = int(self.Text3.get()) #采样帧速率
            settings.isPreview = str2bool(str(self.Text22.get()))
            # 灰度曲线学习参数
            settings.boardPoints_left = int(self.Text5.get()) # 漏板最左点
            settings.boardPoints_right = int(self.Text6.get()) # 漏板最右点
            tempdatas.interval = int((settings.boardPoints_right - settings.boardPoints_left)/6)      
            settings.graythreshold = int(self.Text7.get()) # 正常识别灰度阈值
            settings.errorValue =int(self.Text8.get()) # 学习偏差值
            settings.learningIter = int(self.Text9.get()) # 曲线学习迭代次数
            settings.reconIter = int(self.Text10.get()) # 识别正常拉丝迭代次数
            # 检测相关参数
            settings.threshold = int(self.Text11.get()) # 检测阈值
            settings.areaSet = int(self.Text12.get()) # 面积阈值
            settings.errorNumber = int(self.Text13.get()) # 异常区域个数
            settings.errorTimes = int(self.Text14.get()) # 异常帧数
            settings.typeBreakArea = int(self.Text15.get()) # 异常类型判断
            settings.isShowArea = str2bool(str(self.Text16.get())) # 是否显示异常区域面积
            settings.waitTime = int(self.Text32.get()) # 异常到识别的等待间隔时间                 
            settings.alarmLightTimes = int(self.Text33.get()) # GPIO 
            settings.turnBoardTimes = float(self.Text34.get()) # GPIO
            settings.guasi = str(self.Text17.get()) # 挂丝的个点
            settings.grayAvgValue = str(self.Text35.get()) # 六块的平均灰度值
            # Stove
            settings.stoveName = str(self.Text26.get())#本机炉位名称
            settings.serverIPaddr = str(self.Text29.get())# Socket
            settings.serverPort = int(self.Text30.get())
            settings.nativeIPaddr = str(self.Text27.get())
            settings.nativePort = int(self.Text28.get())
            settings.dayBrokenNum = int(self.Text36.get())
            settings.nightBrokenNum = int(self.Text37.get())
            settings.password = str(self.Text31.get())

            settings.SaveParameters()
            settings.LoadParameters()
            self.update()
            if tk.messagebox.askyesno("提示！","参数设置成功!"):
                pass
        except:
            if tk.messagebox.askyesno("请重试！","参数设置有误!"):
                pass

    def Command2_Cmd(self, event=None):
        #TODO, Please finish the function here!
        '''恢复默认参数'''
        try:
            settings.resolution_width = 2592 # 相机图像分辨率_宽
            settings.resolution_height = 256 # 相机图像分辨率_高
            settings.brightness = 60 # 曝光时间
            settings.capturerate = 30 #采样帧速率
            settings.isPreview = False
            # 灰度曲线学习参数
            #settings.boardPoints_left = 100 # 漏板最左点
            #settings.boardPoints_right = 2200 # 漏板最右点      
            #settings.graythreshold = 8 # 正常识别灰度阈值
            #settings.errorValue =2 # 学习偏差值
            #settings.learningIter = 30 # 曲线学习迭代次数
            #settings.reconIter = 60 # 识别正常拉丝迭代次数
            # 检测相关参数
            settings.threshold = 100 # 检测阈值
            settings.areaSet = 250 # 面积阈值
            settings.errorNumber = 3 # 异常区域个数
            settings.errorTimes = 2 # 异常帧数
            settings.typeBreakArea = 800 # 异常类型判断
            settings.isShowArea = False # 是否显示异常区域面积
            settings.waitTime = 50 # 异常到识别的等待间隔时间                 
            settings.alarmLightTimes = 50 # GPIO 
            settings.turnBoardTimes = 2.5 # GPIO
            #settings.guasi = '0' # 挂丝的个点
            settings.grayAvgValue = [1,2,3,4,5,6] # 六块的平均灰度值
            # Stove
            #settings.stoveName = '313'#本机炉位名称
            #settings.serverIPaddr = '192.254.1.1'# Socket
            #settings.serverPort = 8886
            #settings.nativeIPaddr = '192.254.1.130'
            #settings.nativePort = 8888
            #settings.dayBrokenNum = 0
            #settings.nightBrokenNum = 0
            #settings.password = '666666'
            settings.SaveParameters()
            settings.LoadParameters()
            if tk.messagebox.askyesno("提示！","参数设置成功!"):
                pass
        except:
            if tk.messagebox.askyesno("请重试！","参数设置有误!"):
                pass

    def Command1_Cmd(self, event=None):
        #TODO, Please finish the function here!
        '''调试图像'''
        tempdatas.perviewflag = True
        with picamera.PiCamera() as camera:
            camera.resolution = (settings.resolution_width,settings.resolution_height)
            camera.framerate = settings.capturerate
            camera.brightness = settings.brightness
            camera.hflip=False
            camera.vflip=False
            time.sleep(2)
            camera.start_preview()
            time.sleep(60)
            camera.stop_preview()
            camera.close()
        tempdatas.perviewflag = True

    def Label17_Button_1(self, event):
        #TODO, Please finish the function here!
        pass

    def Text22_Change(self, *args):
        #TODO, Please finish the function here!
        pass


def updatesTextEntry():
    #adf 
    try:
        app.frames[PageFour].update()
    except:
        pass


def str2bool(v):
    '''字符串转bool'''
    return v.lower() in ("yes", "true", "t", "1")


#********************************************************************************
def ask_quit():
    #tk.messagebox.showwarning("警告","密码错误！")
    if tk.messagebox.askyesno("提示！","是否退出程序?"):
        #线程杀死退出
        sys.exit(1)



def SendErrorInfo(senderrorlist):
    try:
        print('len'+str(len(senderrorlist)))
        if len(senderrorlist) != 0:
            for i in range(len(senderrorlist)):
                try:
                    socketC = SocketClient(settings.serverIPaddr,settings.serverPort)
                    socketC.socketConnect()
                    if  socketC.isConnected == True:
                        socketC.sendDateToService(senderrorlist[i][0],senderrorlist[i][1])
                        tempdatas.SendErrorList.pop(i)
                finally:
                    socketC.socketClose()     
    except:
        print('还是异常发送')


def SendInfo(info,cmd):
    try:
        socketC = SocketClient(settings.serverIPaddr,settings.serverPort)
        socketC.socketConnect()
        if  socketC.isConnected == True:
            socketC.sendDateToService(info,cmd)
        else:
            senderrorinfo = [info,cmd]
            tempdatas.SendErrorList.append(senderrorinfo)
    except:
        senderrorinfo = [info,cmd]
        tempdatas.SendErrorList.append(senderrorinfo) 
    finally:
        socketC.socketClose()



#********************************************************************************
# 服务端
def listenClientConnect(socketServer):
    try:
        while True:
            try:
                # 获得conn[连接的套接字]，addr[客户端IP,和端口]
                conn,addr = socketServer.accept()
                print('...................................')
                print('有新客户端进入...',addr)
                try:
                    _thread.start_new_thread(dataReceive, (conn,addr,))
                    print('新客户端进入，开启数据接收新线程......')
                except:
                    print("Error,数据接收新线程无法启动！")
            except:
                pass
    except:
        print('服务器启动失败！')

dataBuffer = bytes()

sn = 0
def dataHandle110(conn):
    global sn
    sn += 1
    #print("第%s个数据包" % sn)
    if tempdatas.rgbFrame != None:
        cv2.imwrite('temp.png',tempdatas.rgbFrame)
        img = cv2.imread('temp.png',cv2.IMREAD_COLOR)
        #img = tempdatas.rgbFrame.copy()
        # 发送图片 open --numpy -- bytes --sendall
        conn.send(b'\n')#头
        conn.send('1990656'.encode())#长度
        conn.send('110'.encode())#命令
        #判断图像是否存在 格式是否正确
        buf = img.ravel()
        conn.send(bytearray(buf))
    else:
        return

def dataHandle120(strbody):
    try:
        settings.guasi = strbody.decode()
        settings.SaveParameters()
        app.frames[PageFour].update()
    except:
        pass

def dataHandle130(conn):
    try:
        updatesoftware()
        cmd = 'sudo reboot'
        subprocess.call(cmd,shell=True)
    except:
        pass

def dataHandle140(bytedatetime):
    try:
        #if datetime.datetime.now() 如果时间相等就不修改了
        strdatetime = bytedatetime.decode()
        cmd = 'sudo date --s=\"' + strdatetime + '\"'
        subprocess.call(cmd,shell=True)
    except:
        pass

#110图像回传命令
#120挂丝设置
#130
#140同步时间
def dataReceive(conn,addr):
    while True:
        data = conn.recv(1)
        print ('包起始标志',data)
        if data == b'\n':
            # 把数据存入缓冲区，类似于push数据,追加到buffer
            data = conn.recv(5)#接收数据长度
            print('包长度',data.decode())
            idatalen = int(data.decode())
            data = conn.recv(idatalen)#命令和包体数据
            cmd = data[0:3]
            body = data[3:]
            print('包体',body.decode())
            if cmd == b'110':
                print('处理110命令......')
                _thread.start_new_thread(dataHandle110,(conn,))
            elif cmd == b'120':
                print('处理120命令......')
                _thread.start_new_thread(dataHandle120,(body,))
            elif cmd == b'130':
                print('处理130命令......')
                _thread.start_new_thread(dataHandle130,(conn,))
            elif cmd == b'140':
                _thread.start_new_thread(dataHandle140,(body,))
            else:
                pass
        elif data == b'':
            print('远端关闭套接字!')
            conn.shutdown(2)
            conn.close()
            break
        else:
            conn.shutdown(2)
            conn.close()
            break

#********************************************************************************
def updatesoftware():
    '''程序升级'''
    try:
        dir_files_list = [
            'FiberWindingCheck.cpython-34.pyc',
            'Settings.pyc',
            'GpioOperate.pyc',
            'SocketClient.pyc',
            'SocketServer.pyc',
            'Switch.pyc',
            'TempDatas.pyc',
            'TftpClient.pyc'
        ]
        save_files_list = [
            '/home/pi/FiberWindingCheck/scripts/FiberWindingCheck.cpython-34.pyc',
            '/home/pi/FiberWindingCheck/scripts/Settings.pyc',
            '/home/pi/FiberWindingCheck/scripts/GpioOperate.pyc',
            '/home/pi/FiberWindingCheck/scripts/SocketClient.pyc',
            '/home/pi/FiberWindingCheck/scripts/SocketServer.pyc',
            '/home/pi/FiberWindingCheck/scripts/Switch.pyc',
            '/home/pi/FiberWindingCheck/scripts/TempDatas.pyc',
            '/home/pi/FiberWindingCheck/scripts/TftpClient.pyc'
            ]
        tftp_client = TftpClient("192.254.1.1",69,dir_files_list,save_files_list)
        tftp_client.downloadFiles()
        if tk.messagebox.askyesno("提示！","升级成功，重新启动检测软件!"):
            cmd = 'sudo reboot'
            subprocess.call(cmd,shell=True)
    except:
        if tk.messagebox.askyesno("提示！","升级失败，请重试!"):
            pass


def pauseCheckReset():
    if tempdatas.iStatus == 2:
        tempdatas.pauseTimes = tempdatas.pauseTimes + 1
        if tempdatas.pauseTimes >= 12:
            imageProcessor.resume() # 恢复正在检测
            tempdatas.runflag = True
            style = Style()
            style.configure('TCommand_RunFlag.TButton', font=('楷体',18,'bold'))
            app.frames[StartPage].Command_RunFlag.configure(style = 'TCommand_RunFlag.TButton')
            app.frames[StartPage].Command_RunFlag.configure(text='正在检测')
            app.frames[StartPage].Command_RunFlag.update()
            tempdatas.pauseTimes = 0
    else:
        tempdatas.pauseTimes = 0
        
#********************************************************************************
def MonitorChannel():
    '''5秒定时器'''
    global imageProvider,socketClient,timer
    if tempdatas.isDead == True:
        imageProvider.stop()
        tempdatas.isDead = False
        imageProvider = ImageProvider() # 采集图像线程
        imageProvider.setDaemon(True) # 设置为守护线程（后台线程）
        imageProvider.start() 
    try:
        pauseCheckReset()
        socketClient = SocketClient(settings.serverIPaddr,settings.serverPort)
        socketClient.socketConnect()
        if  socketClient.isConnected == True:
            ClientInfo = dict(strStoveName=settings.stoveName,iStatus= tempdatas.iStatus)
            try:
                socketClient.sendDateToService(ClientInfo,cmd_ClientInfo)
            finally:
                socketClient.socketClose()
    except:
        pass
    SendErrorInfo(tempdatas.SendErrorList)
    timer = threading.Timer(5,MonitorChannel)
    timer.setDaemon(True)
    timer.start()


def initSystem():
    '''如果程序第一次启动，自动进入检测状态'''
    if tempdatas.runflag == False and tempdatas.perviewflag == False:
        imageProvider.start()  # 开始采集
        imageProcessor.start() # 开始检测
        time.sleep(5)
        tempdatas.runflag = True
        tempdatas.machineStart = True
        tempdatas.condition = iStatus_recongnize
        print('自动进入检测状态！')


def InitParmeButton():
    style = Style()
    if settings.threshold == 100 and settings.areaSet == 300:
        style.configure('level1.TButton',background='blue',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level1.configure(style = 'level1.TButton')
    elif settings.threshold == 100 and settings.areaSet == 250:
        style.configure('level2.TButton',background='blue',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level2.configure(style = 'level2.TButton')
    elif settings.threshold == 95 and settings.areaSet == 300:
        style.configure('level3.TButton',background='blue',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level3.configure(style = 'level3.TButton')
    elif settings.threshold == 95 and settings.areaSet == 250:
        style.configure('level4.TButton',background='blue',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level4.configure(style = 'level4.TButton')
    elif settings.threshold == 90 and settings.areaSet == 250:
        style.configure('level5.TButton',background='blue',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level5.configure(style = 'level5.TButton')
    elif settings.threshold == 90 and settings.areaSet == 200:
        style.configure('level6.TButton',background='blue',text='0',font=('楷体',18,'bold'))
        app.frames[StartPage].level6.configure(style = 'level6.TButton')
    else:
        pass


def isSetGuasi():
    style =  Style()
    if settings.guasi != "0":
        listguasi = settings.guasi.split(",")
        listguasi.pop()#
        for i in range(int(len(listguasi)/2)):
            index = i*2
            print(listguasi[index])
            if settings.boardPoints_left == int(listguasi[index]):
                style.configure('lleft.TButton',background='blue',text='0',font=('楷体',18,'bold'))
                app.frames[StartPage].lleft.configure(style = 'lleft.TButton')
            elif settings.boardPoints_left + tempdatas.interval == int(listguasi[index]):
                style.configure('lright.TButton',background='blue',text='0',font=('楷体',18,'bold'))
                app.frames[StartPage].lright.configure(style = 'lright.TButton')
            elif settings.boardPoints_left + 2*tempdatas.interval == int(listguasi[index]):
                style.configure('midleft.TButton',background='blue',text='0',font=('楷体',18,'bold'))
                app.frames[StartPage].midleft.configure(style = 'midleft.TButton')
            elif settings.boardPoints_left + 3*tempdatas.interval == int(listguasi[index]):
                style.configure('midright.TButton',background='blue',text='0',font=('楷体',18,'bold'))
                app.frames[StartPage].midright.configure(style = 'midright.TButton')
            elif settings.boardPoints_left + 4*tempdatas.interval == int(listguasi[index]):
                style.configure('rleft.TButton',background='blue',text='0',font=('楷体',18,'bold'))
                app.frames[StartPage].rleft.configure(style = 'rleft.TButton')
            elif settings.boardPoints_left + 5*tempdatas.interval == int(listguasi[index]):
                style.configure('rright.TButton',background='blue',text='0',font=('楷体',18,'bold'))
                app.frames[StartPage].rright.configure(style = 'rright.TButton')
            else:
                continue

def initGrayValues():
    if settings.grayAvgValue != '':
        print(settings.grayAvgValue)
        lista = settings.grayAvgValue
        listb = lista.split("[")
        listc = listb[1]
        listd = listc.split("]")
        liste = listd[0]
        listf = liste.split(",")
        listg = [0,0,0,0,0,0]
        for i in range(int(len(listf))):
            listg[i] = float(listf[i])
            settings.spiltPerValues = listg
            tempdatas.spiltPerValues = listg
            print(settings.spiltPerValues)
        #print(listg)



#test
def testTcp():
    try:
        for i in range(100):
            tempdatas.loubanfenbu = [6,6,6,6,6]
            tempdatas.loubanfenbu.append(i)
            BrokenInfo = dict(strStoveName='111',dateTime=str(datetime.datetime.now()),strBrokenType='1',strBrokenArea=tempdatas.loubanfenbu)
            SendInfo(BrokenInfo,cmd_BrokenInfo)
            time.sleep(0.5)
    except:
        print('发送异常！')



#********************************************************************************
iStatus_start = 0
iStatus_learning = 1
iStatus_recongnize = 2
iStatus_normalImage = 3
iStatus_checkImage = 4
iStatus_sendInfo = 5
#********************************************************************************
# 参数初始化
# 字体设置
LARGE_FONT= ("Verdana", 14)
# 命令字
cmd_ClientInfo = "100" # 本机信息
cmd_BrokenInfo = "110" # 断头信息
cmd_ShangtouInfo = "120" # 上头时间
cmd_ShangtouSucess = "130" # 上头成功
newVersion = False # 软件有新版本
windingErrorTimes= [0,0]
mutex = threading.Lock() # 全局互斥锁
#********************************************************************************
#global
SendErrorList = []
#********************************************************************************
#参数初始化
settings = Settings()
settings.LoadParameters()
#临时变量初始化
tempdatas = TempDatas()
#GPIO操作初始化
gpio = GpioOperate()
#客户端
socketClient = SocketClient(settings.serverIPaddr,settings.serverPort)
#相机采集
imageProvider = ImageProvider()
imageProvider.setDaemon(True)
#算法处理
imageProcessor = ImageProcessor()
imageProcessor.setDaemon(True)
#********************************************************************************
channel = 31
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
#下拉，置为低，检测下降沿？
GPIO.setup(channel,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(channel,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def mycallback(chann):
    #可能会调用几次，那么只需要标志位改变一下就可以
    #过10秒在进入检测后，把标志位清除
    #默认的输出为高电平
    tempdatas.machineStart = True
    with open('/home/pi/Desktop/test.txt','a') as my_file:
        my_file.write(str(datetime.datetime.now()) +'按钮被触发\n')
    print('按钮触发！')

#RISING FALLING BOTH
#GPIO.add_event_detect(channel,GPIO.RISING,bouncetime=300)
GPIO.add_event_detect(channel,GPIO.FALLING,bouncetime=300)
#GPIO.add_event_detect(channel,GPIO.BOTH,bouncetime=500)
GPIO.add_event_callback(channel,mycallback)
#********************************************************************************
#********************************************************************************
# 0 InitParmeters           系统参数初始化
# 1 SocketClient            启动Socket客户端
# 2 SocketServer            启动Socket服务器
# 3 TftpClient              启动Tftp客户端
# 4 GpioOperate             GPIO实例化
# 5 ImageProvider           相机开始采集图像
# 6 ImageProcessor          执行图像处理算法
# 7 Application             启动系统主界面
#********************************************************************************
#********************************************************************************
if __name__ == '__main__':
# InitParmeters           系统参数初始化
    print('系统启动中......')
    print('加载配置参数......')
    app = Application() # 实例化Application，并启动消息循环
    tempdatas.interval = int((settings.boardPoints_right - settings.boardPoints_left)/6)
    initGrayValues()
    isSetGuasi()
    InitParmeButton()
    # SocketClient            启动Socket客户端
    socketClient.socketConnect()
    if  socketClient.isConnected == True:
        ClientInfo = dict(strStoveName=settings.stoveName,iStatus= tempdatas.iStatus)
        try:
            socketClient.sendDateToService(ClientInfo,cmd_ClientInfo)
        finally:
            socketClient.socketClose()
    # 接收连接成功消息
    # 准备组包发送数据
    # SocketClient            启动Socket服务端
    try:
        socketS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定IP地址以及端口号
        socketS.bind((settings.nativeIPaddr, settings.nativePort))
        # 设置最多几个排队请求
        socketS.listen(10)
        # 开始侦听
        _thread.start_new_thread(listenClientConnect, (socketS,))
        print('start server sussess!')
    except:
        print('start server error!')

    timer=threading.Timer(5,MonitorChannel) # 定时器开启
    timer.setDaemon(True)
    timer.start()

    timer=threading.Timer(30,initSystem) 
    timer.setDaemon(True)
    timer.start()

    app.title('拉丝断头检测系统')
    #app.iconbitmap('pygame.ico')
    app.geometry('800x480+0+0') # width x height + xoffset +yoffset
    #app.master.title('慧眼一号-拉丝检测系统') # 设置窗口标题
    app.protocol("WM_DELETE_WINDOW",ask_quit)
    app.mainloop() # 主消息循环
