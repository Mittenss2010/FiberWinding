#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import socket,time
import json
import numpy as np
import sys
import threading
import _thread


class SocketClient(object):
    '''Socket--客户端'''
    def __init__(self,ipaddr,port):
        '''初始化'''
        self.socketClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #self.socketClient.settimeout(3)
        self.ipaddr = ipaddr
        self.port = port
        self.isConnected = False
    

    def socketConnect(self):
        '''Socekt--连接服务器--返回连接状态'''
        try:
            self.socketClient.connect((self.ipaddr,self.port))
            self.isConnected = True
            print('连接服务器成功！',self.ipaddr)
            #_thread.start_new_thread(ReceiveData,(self.socketClient,))
        except:
            self.isConnected = False
            print('连接服务器失败！',self.ipaddr,self.port)
    

    def sendDateToService(self,jsonData,Cmd):
        '''组包发送数据'''
        try:
            # 接收欢迎消息:
            # print (socketClient.recv(5).decode())
            # 包体长度 + 包类型 + 命令 + 包体
            # 包体长度
            body = json.dumps(jsonData)
            ilen = len(body)
            strlen =''
            for i in range(0,7-len(str(ilen))):
                strlen = strlen + '0'
            strlen = strlen + str(ilen)
            strCmd = Cmd
            strPackage = strlen + strCmd + body
            print(strPackage)
            self.socketClient.sendall(strPackage.encode())
        except:
            pass
    

    def socketClose(self):
        '''关闭Socket'''
        if self.isConnected == True:
            self.socketClient.shutdown(2)
            self.socketClient.close()
            self.isConnected = False
            print('Socket套接字关闭！')
        else:
            return


    def ReceiveData(self):
        ''''''
        while isConnected:
            try:
                RevDataPacket(socket)
            except:
                isConnected = False


    def RevDataPacket(self):
        ''''''
        print(socket.recv(1))
        pass









if __name__ == '__main__':
    '''asdf'''
    socketClient = SocketClient('192.254.1.1',8886)
    socketClient.socketConnect()
    if  socketClient.isConnected == True:
        BrokenInfo = dict(strStoveName='313',dateTime='2017-09-11 14-04-22',strBrokenType='1',strBrokenArea='3')
        try:
            socketClient.sendDateToService(BrokenInfo,'110')
            print('send is over')
        finally:
            socketClient.socketClose()




            
    BrokenInfo = dict(strStoveNmae='313',dateTime='2017-09-11 14-04-22',strBrokenType='1',strBrokenArea='3')
    sendDateToService(connectSocket('192.254.1.1',8886),BrokenInfo,'110')
    sendDateToService(connectSocket('192.254.1.1',8886),BrokenInfo,'110')
    s = connectSocket('192.168.0.127',4444)
    print(s)
    SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 建立连接:
    s.connect(('192.168.0.127', 4444))
    # 接收欢迎消息:
    #print (s.recv(SIZE).decode())

    # 发送字符串
    #s.send('000005'.encode())
    #s.send('c'.encode())
    #s.send('hello'.encode())

    # 发送字符串
    #s.send('000039'.encode())
    #s.send('c'.encode())
    #msg = 'hello , i am new client,i am coming!...'
    #s.send(msg.encode())

    # 发送Json 本机（客户端）信息ClientInfo
    # 获得发送Json字符串的长度
    s.send('0000071'.encode())
    s.send('j'.encode())
    s.send('1'.encode()) # 命令包序号
    ClientInfo = dict(strStoveName ='313',strIpAddress='192.168.0.127',iPort=8885)
    cmd = json.dumps(ClientInfo)
    ob = json.loads(cmd)
    print(ob)
    print(ob['strStoveName'])
    s.sendall(cmd.encode()) 
    time.sleep(2)
    s.close()

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('192.168.0.127',4444))
    # 发送Json 一次异常数据
    BrokenInfo = dict(strStoveNmae='313',dateTime='2017-09-11 14-04-22',strBrokenType='1',strBrokenArea='3')
    cmd = json.dumps(BrokenInfo)
    ilen = len(cmd)

    strlen = ''
    for i in range(0,7-len(str(ilen))):
        strlen =strlen + '0' 
    strlen = strlen + str(ilen)
    s.send(strlen.encode())
    s.send('j'.encode())
    s.send('2'.encode())
    s.sendall(cmd.encode())
    s.close()
