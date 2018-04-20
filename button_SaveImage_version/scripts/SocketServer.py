
import sys
import socket
import struct #为了实现打包struct.pack()和拆包struct.unpack()数据\
import threading
import _thread

class SocketServer(object):
    '''Socket 服务端'''

    def __init__(self,ipaddr,port):
        '''Socket 服务端 初始化'''
        self.ipaddr = ipaddr
        self.port =port
        self.SocketServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    sn = 0
    def dataHandle(self,conn):
        while True:
            global sn 
            sn += 1
            print("")

    def dataReveive(self,conn,addr):
        '''数据接收处理'''
        print('Connected by ',addr)
        data = conn.recv(1)
        print('包起始标识',data)
        if data == b'\n':
            # 把数据存入缓冲区，类似于push数据,追加到buffer
            data = conn.recv(5)#接收数据长度
            print('包长度',data.decode())
            idatalen = int(data.decode())
            data = conn.recv(idatalen)#命令和包体数据
            cmd = data[0:3]
            print(cmd)
            print('命令',cmd.decode())
            body = data[3:]
            print('包体',body.decode())
            if cmd == b'110':
                dataHandle(conn)
            elif cmd == b'111':
                pass
            elif cmd == b'112':
                pass
            elif cmd == b'113':
                pass
            else:
                pass
        else:
            print('Is not head!')

    def start(self):
        '''socket 连接'''
        self.SocketServer.bind((self.ipaddr,self.port))
        self.SocketServer.listen(10)
        while True:
            conn,addr = self.SocketServer.accept()
            try:
                _thread.start_new_thread(dataReveive,(conn,addr,))
            except:
                print("Error,线程无法启动")





if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    print(host)
    Socketserver = SocketServer('192.168.137.1',8888)
    Socketserver.start()
