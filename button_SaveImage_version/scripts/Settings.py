import os, sys
import configparser

class Settings(object):
    '''conf 文件操作 http://www.cnblogs.com/victorwu/p/5762931.html'''
    def __init__(self):
        # 相机参数
        self.resolution_width = 2592 # 相机图像分辨率_宽
        self.resolution_height = 256 # 相机图像分辨率_高
        self.brightness = 55 # 曝光时间
        self.capturerate = 30 #采样帧速率
        self.isPreview = False
        # 灰度曲线学习参数
        self.boardPoints_left = 100 # 漏板最左点
        self.boardPoints_right = 2200 # 漏板最右点      
        self.graythreshold = 10 # 正常识别灰度范围
        self.errorValue = 2 # 学习偏差值
        self.learningIter = 50 # 曲线学习迭代次数
        self.reconIter = 60 # 识别正常拉丝迭代次数
        self.grayAvgValue = [1,2,3,4,5,6] # 六块的平均灰度值
        # 检测相关参数
        self.threshold = 80 # 检测阈值
        self.areaSet = 250 # 面积阈值
        self.errorNumber = 3 # 异常区域个数
        self.errorTimes = 3 # 异常帧数
        self.typeBreakArea = 1000 # 异常类型判断
        self.isShowArea = False # 是否显示异常区域面积
        self.waitTime = 50 # 异常到识别的等待间隔时间                 
        self.guasi = [0,0] # 挂丝的个点
        self.alarmLightTimes = 50 # GPIO 
        self.turnBoardTimes = 2.5 # GPIO
      
        # Stove
        self.stoveName = '301'
        self.serverIPaddr = '192.254.1.1'# Socket
        self.serverPort = 8886
        self.nativeIPaddr = '192.254.1.101'
        self.nativePort = 8888
        self.dayBrokenNum = 0
        self.nightBrokenNum = 0
        self.password = '666666'

    def SaveParameters(self):
        '''保存参数'''
        try:
            exepath = os.path.dirname(sys.path[0])
            path = exepath + "/configure/Appconfig.conf"     
            print(path)  
            conf = configparser.SafeConfigParser()
            conf.read(path)
            #[CameraParmeters] 5
            conf.set('cameraparmeters','resolution_width',str(self.resolution_width))
            conf.set('cameraparmeters','resolution_height',str(self.resolution_height))
            conf.set('cameraparmeters','brightness',str(self.brightness))
            conf.set('cameraparmeters','capturerate',str(self.capturerate))
            conf.set('cameraparmeters','isPreview',str(self.isPreview))
            # [learning] 7
            conf.set('learning','boardpoints_left',str(self.boardPoints_left))
            conf.set('learning','boardpoints_right',str(self.boardPoints_right))
            conf.set('learning','graythreshold',str(self.graythreshold))
            conf.set('learning','errorvalue',str(self.errorValue))
            conf.set('learning','learningiter',str(self.learningIter))
            conf.set('learning','reconiter',str(self.reconIter))
            conf.set('learning','grayavgvalue',str(self.grayAvgValue))
            # [CheckParmeters]
            conf.set('CheckParmeters','threshold',str(self.threshold))
            conf.set('CheckParmeters','areaset',str(self.areaSet))
            conf.set('CheckParmeters','errornumber',str(self.errorNumber))
            conf.set('CheckParmeters','errortimes',str(self.errorTimes))
            conf.set('CheckParmeters','typebreakarea',str(self.typeBreakArea))
            conf.set('CheckParmeters','isshowarea',str(self.isShowArea))
            conf.set('CheckParmeters','waittime',str(self.waitTime))
            conf.set('CheckParmeters','guasi',str(self.guasi))
            conf.set('CheckParmeters','alarmlighttimes',str(self.alarmLightTimes))
            conf.set('CheckParmeters','turnboardtimes',str(self.turnBoardTimes))
            
            # [Stove]
            conf.set('Stove','stovename',str(self.stoveName))
            conf.set('Stove','serveripaddr',str(self.serverIPaddr))
            conf.set('Stove','serverport',str(self.serverPort))
            conf.set('Stove','nativeipaddr',str(self.nativeIPaddr))
            conf.set('Stove','nativeport',str(self.nativePort))
            conf.set('Stove','daybrokennum',str(self.dayBrokenNum))
            conf.set('Stove','nightbrokennum',str(self.nightBrokenNum))
            conf.set('Stove','password',str(self.password)) 

            conf.write(open(path, 'w'))
            conf.write(sys.stdout)
        except:
            print('error ')
            pass


    def UpdateParameters(self):
        '''更新参数'''
        pass

    def LoadParameters(self):
        '''载入参数'''
        try:
            exepath = os.path.dirname(sys.path[0])
            path = exepath + "/configure/Appconfig.conf"
            conf = configparser.SafeConfigParser()
            conf.read(path)
            #self.isPreview = conf.getboolean('tempdata','perviewflag')
            #self.isPreview = conf.getint('tempdata','perviewflag')
            self.resolution_width = conf.getint('cameraparmeters','resolution_width') # 相机图像分辨率_宽
            self.resolution_height = conf.getint('cameraparmeters','resolution_height') # 相机图像分辨率_高
            self.brightness = conf.getint('cameraparmeters','brightness') # 曝光时间
            self.capturerate = conf.getint('cameraparmeters','capturerate') #采样帧速率
            self.isPreview = conf.getboolean('cameraparmeters','ispreview')
            # 灰度曲线学习参数
            self.boardPoints_left = conf.getint('learning','boardpoints_left') # 漏板最左点
            self.boardPoints_right = conf.getint('learning','boardpoints_right') # 漏板最右点      
            self.graythreshold = conf.getint('learning','graythreshold') # 正常识别灰度范围
            self.errorValue = conf.getint('learning','errorvalue') # 学习偏差值
            self.learningIter = conf.getint('learning','learningiter') # 曲线学习迭代次数
            self.reconIter = conf.getint('learning','reconiter') # 识别正常拉丝迭代次数
            self.grayAvgValue = conf.get('learning','grayavgvalue') # 六块的平均灰度值 grayavgvalue
            # 检测相关参数
            self.threshold = conf.getint('CheckParmeters','threshold') # 检测阈值
            self.areaSet = conf.getint('CheckParmeters','areaset') # 面积阈值
            self.errorNumber = conf.getint('CheckParmeters','errornumber') # 异常区域个数
            self.errorTimes = conf.getint('CheckParmeters','errortimes') # 异常帧数
            self.typeBreakArea = conf.getint('CheckParmeters','typebreakarea') # 异常类型判断
            self.isShowArea = conf.getboolean('CheckParmeters','isshowarea') # 是否显示异常区域面积
            self.waitTime = conf.getint('CheckParmeters','waittime') # 异常到识别的等待间隔时间                 
            self.guasi = conf.get('CheckParmeters','guasi') # 挂丝的个点
            self.alarmLightTimes = conf.getint('CheckParmeters','alarmlighttimes') # GPIO 
            self.turnBoardTimes = conf.getfloat('CheckParmeters','turnboardtimes') # GPIO
        
            # Stove
            self.stoveName = conf.get('Stove','stovename')
            self.serverIPaddr = conf.get('Stove','serveripaddr')# Socket
            self.serverPort = conf.getint('Stove','serverport')
            self.nativeIPaddr = conf.get('Stove','nativeipaddr')
            self.nativePort = conf.getint('Stove','nativeport')
            self.dayBrokenNum = conf.getint('Stove','daybrokennum')
            self.nightBrokenNum = conf.getint('Stove','nightbrokennum')
            self.password = conf.get('Stove','password')
        except:
            if tk.messagebox.askyesno("警告！","参数加载异常!"):
                pass

    def initParmeters(self):
        '''参数保存'''
        try:
            #exeruningpath=os.path.dirname(sys.executable)
            exepath = os.path.dirname(sys.path[0])
            path = exepath + "/configure/Appconfig.conf"
            conf = configparser.SafeConfigParser()
            conf.read(path)
            brightness = conf.getint('CameraParmeters', 'Brightness')
            print(str(brightness))
            threshold = conf.getint('CameraParmeters', 'Thershold')
            print(str(threshold))
            areaSet = conf.getint('CameraParmeters', 'Area')
            errorNumberSet = conf.getint('CameraParmeters', 'ErrorNumber')
            errorTimesSet = conf.getint('CameraParmeters', 'ErrorTimes')
            previewTime = conf.getint('CameraParmeters', 'previewtime')
        except:
            pass

if __name__ == '__main__':
    setting = Settings()
    setting.SaveParameters()
    print(setting)
