from threading import Thread
from socket import *
import struct

def upload(filename,user_ip,user_port):
    num = 0
    f = open(filename,'ab') 
    s_up = socket(AF_INET,SOCK_DGRAM)
    send_data_1 = struct.pack("!HH",4,num)
    s_up.sendto(send_data_1,(user_ip,user_port))  #第一次用随机端口发送

    while True:
        recv_data,user_info = s_up.recvfrom(1024)  #第二次客户连接我随机端口
        caozuohao_up,ack_num = struct.unpack('!HH',recv_data[:4])
        print(caozuohao_up,ack_num,num)
        if int(caozuohao_up) == 3 and ack_num == num :
            f.write(recv_data[4:])
            send_data = struct.pack("!HH",4,num)
            s_up.sendto(send_data,(user_ip,user_port)) #第二次我用随机端口发
            num = num + 1
            if len(recv_data) < 516:
                print(user_ip+'上传文件'+filename+':完成')
                f.close()
                exit()
     
def download(filename,user_ip,user_port):
    s_down = socket(AF_INET, SOCK_DGRAM)
    num = 0

    try:
        f = open(filename,'rb')
    except:
        error_data = struct.pack('!HHHb',5,5,5,num)
        s_down.sendto(error_data, (user_ip,user_port))  #文件不存在时发送
        exit()  #只会退出此线程

    while True:
        read_data = f.read(512)
        send_data = struct.pack('!HH',3,num) + read_data
        s_down.sendto(send_data, (user_ip,user_port))  #数据第一次发送
        if len(read_data) < 512:
            print('传输完成, 对方下载成功')
            exit()        
        recv_ack =  s_down.recv(1024)  #第二次接收
        caozuoma,ack_num = struct.unpack("!HH", recv_ack)
#        print(caozuoma,ack_num,len(read_data))
        num += 1
        if int(caozuoma) != 4 or int(ack_num) != num-1 :
            exit()
    f.close()

s = socket(AF_INET,SOCK_DGRAM)
s.bind(('',69))

def main():
    while 1:
        recv_data,(user_ip,user_port) = s.recvfrom(1024)  #第一次客户连接69端口
        print(recv_data, user_ip, user_port)
        if struct.unpack('!b5sb',recv_data[-7:]) == (0, b'octet', 0):
            caozuoma = struct.unpack('!H',recv_data[:2])
            filename = recv_data[2:-7].decode('gb2312')
            if caozuoma[0] == 1:
                print('对方想下载数据',filename)
                t = Thread(target = download, args = (filename,user_ip,user_port)) 
                t.start()           
            elif caozuoma[0] == 2:
                print('对方想上传数据',filename)
                t = Thread(target = upload, args = (filename,user_ip,user_port)) 
                t.start()           

if __name__ == '__main__':
    main()