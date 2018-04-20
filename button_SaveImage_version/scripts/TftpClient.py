#! /usr/bin/env python3
# -*- coding:utf-8 -*- 

from socket import *
import struct #为了实现打包struct.pack()和拆包struct.unpack()数据
import sys

# python3 05-xx.py 192.168.105.125 bb.jpg
class TftpClient(object):
    ''' TFTP下载文件'''

    def __init__(self,ipaddr,port,dirfiles,savefiles):
        '''构造函数：参数初始化'''
        self.ipaddr = ipaddr            # 服务端IP地址
        self.port = port                # 服务端端口号
        self.dirfiles = dirfiles        # 目标文件（List）
        self.savefiles = savefiles      # 保存路径（List）

    def __del__(self):
        '''析构'''
        pass

    def downloadFiles(self):
        '''下载文件'''
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        server_addr = (self.ipaddr,self.port)

        for items in range(0,len(self.dirfiles),1):
            print(str(items))
            print(len(self.dirfiles))
            # 打包数据
            # !表示网络字节序,H表示2bytes无符号整数
            # 5s表示长度为5字符串 
            # B表示1byte的无符号整数
            fmt = '!H%dsB5sB' % len(self.dirfiles[items])
            send_data = struct.pack(fmt,1,self.dirfiles[items].encode() ,0,b'octet',0)
            #send_data = struct.pack(fmt,1,file_name ,0,b'octet',0)
            udp_socket.sendto(send_data,server_addr)
            filewrite =  None # 文件对象
            #上一次blockNum
            lastBlockNum = 0
        
            # 循环接收和应答
            while True:
                recv_data,peer_addr = udp_socket.recvfrom(1024)
                # 拆包数据，解包处理
                opcode,blockNum = struct.unpack('!HH',recv_data[:4])

                if opcode == 3: # 表示数据包
                    # 写入文件
                    # 1打开文件
                    # 第一次收到服务器发送数据包
                    if blockNum == 1: 
                        filewrite = open(self.savefiles[items],'wb')

                    # 拆出数据
                    data_fmt = '!%ds' % (len(recv_data) - 4)
                    data_content = struct.unpack(data_fmt, recv_data[4:])

                    # 写入文件之前判断写过没有
                    # if 这一次blockNum == 上一次blockNum + 1
                    if lastBlockNum + 1 == blockNum:
                        #print(data_content[0])
                        filewrite.write(data_content[0]) # 拆出来是元组,bytes对象,write时候需要str字符串

                    # 打包应答数据
                    ack_data = struct.pack('!HH',4,blockNum)
                    udp_socket.sendto(ack_data,peer_addr) # 不能再给server_addr，因为端口号变了

                    # 当应答完毕，更新lastBlockNum(数据包标识)
                    lastBlockNum = blockNum
                    print(lastBlockNum)
                    # 如果数据长度小于 2 + 2 + 512 传输结束
                    if len(recv_data) < 516:
                        print('over')
                        filewrite.close()
                        break
                elif opcode == 5:# 出错
                    err_num = blockNum
                    # 拆出错误信息
                    fmt = "!%ds" % (len(recv_data) - 5)
                    err_msg = struct.unpack(fmt,recv_data[4:-1])
                    print('出错信息:%s' % err_msg)
                    break

if __name__ == '__main__':
    # 目标文件
    dir_files_list = [
        'mima.py',
        '1.bmp'
        ]
    
    save_files_list = [
        'mimmm.py',
        '111.bmp'
        ]
    tftp_client = TftpClient("192.168.137.1",69,dir_files_list,save_files_list)
    tftp_client.downloadFiles()
