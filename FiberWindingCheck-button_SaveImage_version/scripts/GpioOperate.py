#********************************************************************************
'''Less then 80 words'''
'''2017-10-7 16:01'''
'''Code by Charwee'''
#********************************************************************************
import os, sys
import threading
import time
import datetime
import RPi.GPIO as GPIO



class GpioOperate(object):
    '''GPIO 操作'''
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        #self.INPUT = 31
        self.ALARME = 33
        self.STOPMACHINE = 35
        self.TURNBOARD = 37
        '''构造函数：GPIO口参数初始化'''
        #GPIO.setmode(GPIO.BOARD)
        # 消除告警信号
        GPIO.setwarnings(False)
        # 33，控制报警灯
        GPIO.setup(self.ALARME,GPIO.OUT,initial=GPIO.LOW)
        # 35，控制开机停机
        GPIO.setup(self.STOPMACHINE,GPIO.OUT,initial=GPIO.LOW)
        # 37，控制翻板动作
        GPIO.setup(self.TURNBOARD,GPIO.OUT,initial=GPIO.LOW)
        # 上拉设置
        #GPIO.setup(self.INPUT,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        # 下拉设置
        #GPIO.setup(INPUT,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    def ALARME_Start(self):
        '''报警灯开启'''
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.ALARME,GPIO.OUT,initial=GPIO.LOW)
        GPIO.output(self.ALARME,GPIO.HIGH)

    def ALARME_Stop(self):
        '''报警灯关闭'''
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.ALARME,GPIO.OUT,initial=GPIO.LOW)
        GPIO.output(self.ALARME,GPIO.LOW)

    def Machine_Stop(self):
        '''停机信号启动'''
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            GPIO.setup(self.STOPMACHINE,GPIO.OUT,initial=GPIO.LOW)
            GPIO.output(self.STOPMACHINE,GPIO.HIGH)
            with open('/home/pi/Desktop/test.txt','a') as my_file:
                my_file.write('GPIO.output(self.STOPMACHINE,GPIO.HIGH)\n')
            time.sleep(0.2)
            GPIO.output(self.STOPMACHINE,GPIO.LOW)
            with open('/home/pi/Desktop/test.txt','a') as my_file:
                my_file.write('GPIO.output(self.STOPMACHINE,GPIO.LOW)\n')
            #GPIO.cleanup(self.STOPMACHINE)
        except Exception as e:
            with open('/home/pi/Desktop/test.txt','a') as my_file:
                my_file.write('停机信号操作异常')
        finally:
            GPIO.output(self.STOPMACHINE,GPIO.LOW)
    
    def TurnBoard_Start(self,delay):
        '''翻板控制'''
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            GPIO.setup(self.TURNBOARD,GPIO.OUT,initial=GPIO.LOW)
            GPIO.output(self.TURNBOARD,GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.TURNBOARD,GPIO.LOW)
            #GPIO.cleanup(self.TURNBOARD)
        except Exception as e:
            with open('/home/pi/Desktop/test.txt','a') as my_file:
                my_file.write('翻板控制操作异常')
        finally:
            GPIO.output(self.TURNBOARD,GPIO.LOW)


    def InitGPIOLOW(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.output(self.TURNBOARD,GPIO.LOW)
        GPIO.output(self.STOPMACHINE,GPIO.LOW)
        GPIO.output(self.ALARME,GPIO.LOW)

if __name__ == '__main__':
    gpio = GpioOperate()
    gpio.ALARME_Start()
    time.sleep(1)
    gpio.ALARME_Stop()
