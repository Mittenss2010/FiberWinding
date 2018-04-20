# -*- coding: utf-8 -*-
#python 27
#xiaodeng
#python之模块ftplib(FTP协议的客户端)



#需求：快速进行ftp上传 ，下载，查询文件

from ftplib import FTP
ftp = FTP()                                     #设置变量

timeout = 3000  
port = 69

ftp.connect('192.168.0.103',port,timeout)       # 连接FTP服务器
#ftp.login('UserName','888888')                  # 登录

print(ftp.getwelcome())                        # 获得欢迎信息

ftp.cwd('C:/Users/Charwee/Desktop/长度图')                            # 设置FTP远程目录(路径)  
list = ftp.nlst()                               # 获取目录下的文件,获得目录列表  
for name in list:  
    print(name)
path = 'd:/data/' + name                        # 定义文件保存路径  
f = open(path,'wb')                             # 打开要保存文件  
filename = 'RETR ' + name                       # 保存FTP文件  
ftp.retrbinary(filename,f.write)                # 保存FTP上的文件  
ftp.delete(name)                                # 删除FTP文件  
ftp.storbinary('STOR '+filename, open(path, 'rb')) # 上传FTP文件  
ftp.quit()

'''
    Example:
    >>> from ftplib import FTP
    >>> ftp = FTP('ftp.python.org') #连接ftp服务器;connect to host, default port
    >>> ftp.login()                 # default, i.e.: user anonymous, passwd anonymous@
    '230 Guest login ok, access restrictions apply.'
    >>> ftp.retrlines('LIST')       # list directory contents
    total 9
    drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 .
    drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 ..
    drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 bin
    drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 etc
    d-wxrwxr-x   2 ftp      wheel        1024 Sep  5 13:43 incoming
    drwxr-xr-x   2 root     wheel        1024 Nov 17  1993 lib
    drwxr-xr-x   6 1094     wheel        1024 Sep 13 19:07 pub
    drwxr-xr-x   3 root     wheel        1024 Jan  3  1994 usr
    -rw-r--r--   1 root     root          312 Aug  1  1994 welcome.msg
    '226 Transfer complete.'
    >>> ftp.quit()                  #断开服务器连接
    '221 Goodbye.'
    

    class FTP
        ftp=FTP()                                      #设置变量，类似于初始化        
     |  An FTP client class.
     
     |  Methods:
     |  acct(self, password)
     |      Send new account name.
     |  
     |  close(self)                                     #close连接
     |      Close the connection without assuming anything about it.
     |  
     |  connect(self, host='', port=0, timeout=-999)    #连接的ftp sever和端口，如：ftp.connect('192.168.1.188',21,30) 
     |  
     |  cwd(self, dirname)                              #把当前目录设置为path,设置FTP当前操作的路径
     |      Change to a directory.
     |  
     |  debug = set_debuglevel(self, level)             #ftp.set_debuglevel(2) #打开调试级别2，显示详细信息
     |  
     |  delete(self, filename)                          #删除远程文件
     |      Delete a file.
     |  
     |  dir(self, *args)                                #显示目录下文件信息
     |      List a directory in long form.
     |      By default list current directory to stdout.
     |      Optional last argument is callback function; all
     |      non-empty arguments before it are concatenated to the
     |      LIST command.  (This *should* only be used for a pathname.)
     |  
     |  getline(self)                                   #从服务器输出一行数据
     |      # Internal: return one line from the server, stripping CRLF.
     |      # Raise EOFError if the connection is closed
     |  
     |  getmultiline(self)
     |      # Internal: get a response from the server, which may possibly
     |      # consist of multiple lines.  Return a single string with no
     |      # trailing CRLF.  If the response consists of multiple lines,
     |      # these are separated by '\n' characters in the string
     |  
     |  getresp(self)
     |      # Internal: get a response from the server.
     |      # Raise various errors if the response indicates an error
     |  
     |  getwelcome(self)                                #打印出欢迎信息
     |      Get the welcome message from the server.
     |      (this is read and squirreled away by connect())
     |  
     |  login(self, user='', passwd='', acct='')    #登录到FTP服务器，所有的参数都是可选的.
     |      Login, default anonymous.
     |  
     |  makepasv(self)
     |  
     |  makeport(self)                              #创建一个新的套接字，并发送一个端口命令。
     |      Create a new socket and send a PORT command for it.
     |  
     |  mkd(self, dirname)                          #创建远程目录；建立一个目录，返回其完整路径名
     |      Make a directory, return its full pathname.
     |  
     |  nlst(self, *args)                           #与dir()类似，但返回一个文件名的列表，而不是显示这些文件名
                                                    #返回给定目录下的文件列表（默认情况下）
     |      Return a list of files in a given directory (default the current).
     |  
     |  ntransfercmd(self, cmd, rest=None)
     |      Initiate a transfer over the data connection.
     |      
     |      If the transfer is active, send a port command and the
     |      transfer command, and accept the connection.  If the server is
     |      passive, send a pasv command, connect to it, and start the
     |      transfer command.  Either way, return the socket for the
     |      connection and the expected size of the transfer.  The
     |      expected size may be None if it could not be determined.
     |      
     |      Optional `rest' argument can be a string that is sent as the
     |      argument to a REST command.  This is essentially a server
     |      marker used to tell the server to skip over any data up to the
     |      given marker.
     |  
     |  putcmd(self, line)
     |      # Internal: send one command to the server (through putline())
     |  
     |  putline(self, line)
     |      # Internal: send one line to the server, appending CRLF
     |  
     |  pwd(self)                                   #当前工作目录
     |      Return current working directory.
     |  
     |  quit(self)                                  #退出ftp
     |      Quit, and close the connection.
     |  
     |  rename(self, fromname, toname)              #改文件名，把远程文件fromname 改名为toname
     |      Rename a file.
     |  
     |  retrbinary(self, cmd, callback, blocksize=8192, rest=None)
                                                     #与retrlines()类似，只是这个指令处理二进制文件。回调函数
     |      Retrieve data in binary mode.  A new port is created for you.
     |      
     |      Args:
     |        cmd: A RETR command.
     |        callback: A single parameter callable to be called on each
     |                  block of data read.
     |        blocksize: The maximum number of bytes to read from the
     |                   socket at one time.  [default: 8192]
     |        rest: Passed to transfercmd().  [default: None]
     |      
     |      Returns:
     |        The response code.
     |  
     |  retrlines(self,cmd,callback=None)         #
                                                  #ftp.retrlines('LIST')#返回目录内容
                                                  #此时可以获得当前ftp目录下的所有文件的信息
     |      Retrieve data in line mode.  A new port is created for you.
     |      
     |      Args:
     |        cmd: A RETR, LIST, NLST, or MLSD command.
     |        callback: An optional single parameter callable that is called
     |                  for each line with the trailing CRLF stripped.
     |                  [default: print_line()]
     |      
     |      Returns:
     |        The response code.
     |  
     |  rmd(self, dirname)  #删除远程目录                    
     |      Remove a directory.
     |  
     |  sanitize(self, s)
     |      # Internal: "sanitize" a string for printing
     |  
     |  sendcmd(self, cmd)
     |      Send a command and return the response.
     |  
     |  sendeprt(self, host, port)
     |      Send a EPRT command with the current host and the given port number.
     |  
     |  sendport(self, host, port)
     |      Send a PORT command with the current host and the given
     |      port number.
     |  
     |  set_debuglevel(self, level)
                                    #ftp.set_debuglevel(2) #打开调试级别2，显示详细信息
                                    #ftp.set_debuglevel(0) #关闭调试模式    
     |      Set the debugging level.
     |      The required argument level means:
     |      0: no debugging output (default)
     |      1: print commands and responses but not body text etc.
     |      2: also print raw lines read and sent before stripping CR/LF
     |  
     |  set_pasv(self, val)
     |      Use passive or active mode for data transfers.
     |      With a false argument, use the normal PORT mode,
     |      With a true argument, use the PASV command.
     |  
     |  size(self, filename)    #检索文件大小
     |      Retrieve the size of a file.
     |  
     |  storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None)
                                 #上传FTP文件
                                 #ftp.storbinaly("STOR filename.txt",file_handel,bufsize) #上传目标文件
                                 #ftp.storbinary('STOR '+filename, open(path, 'rb')) # 上传FTP文件
                                 #注意storlines的解释
                                 #只是这个指令处理二进制文件。要给定一个文件对象f，上传块大小bs 默认为8Kbs=8192])
     |      Store a file in binary mode.  A new port is created for you.
     |      
     |      Args:
     |        cmd: A STOR command.
     |        fp: A file-like object with a read(num_bytes) method.
     |        blocksize: The maximum data size to read from fp and send over
     |                   the connection at once.  [default: 8192]
     |        callback: An optional single parameter callable that is called on
     |                  each block of data after it is sent.  [default: None]
     |        rest: Passed to transfercmd().  [default: None]
     |      
     |      Returns:
     |        The response code.
     |  
     |  storlines(self, cmd, fp, callback=None)
                                 #storlines(cmd, f)
                                 #给定FTP 命令（如“STOR filename”），以上传文本文件。要给定一个文件对象f
     |      Store a file in line mode.  A new port is created for you.
     |      
     |      Args:
     |        cmd: A STOR command.
     |        fp: A file-like object with a readline() method.
     |        callback: An optional single parameter callable that is called on
     |                  each line after it is sent.  [default: None]
     |      
     |      Returns:
     |        The response code.
     |  
     |  transfercmd(self, cmd, rest=None)
     |      Like ntransfercmd() but returns only the socket.
     |  
     |  voidcmd(self, cmd)
     |      Send a command and expect a response beginning with '2'.
     |  
     |  voidresp(self)
     |      Expect a response beginning with '2'.

DATA
    __all__ = ['FTP', 'Netrc', 'FTP_TLS']
'''