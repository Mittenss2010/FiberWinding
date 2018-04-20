#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys
if sys.version_info[0] == 2:
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    #Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    #Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    #import tkFileDialog
    #import tkSimpleDialog
else:  #Python 3.x
    import tkinter as tk
    from tkinter import *
    from tkinter.font import Font
    from tkinter.ttk import *
    import tkinter.messagebox
    #import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()


class Application_ui(tk.Frame):
    # 这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self,parent,root):
        super().__init__(parent)
        self.root = root
        self.createWidgets(root)

    def createWidgets(self,root):
        self.style = Style()

        self.style.configure('TFrame3.TLabelframe', font=('宋体',9))
        self.style.configure('TFrame3.TLabelframe.Label', font=('宋体',9))
        self.Frame3 = LabelFrame(self, text='', style='TFrame3.TLabelframe')
        self.Frame3.place(relx=0.01, rely=0.717, relwidth=0.881, relheight=0.252)

        self.style.configure('TFrame2.TLabelframe', font=('宋体',9))
        self.style.configure('TFrame2.TLabelframe.Label', font=('宋体',9))
        self.Frame2 = LabelFrame(self, text='', style='TFrame2.TLabelframe')
        self.Frame2.place(relx=0.01, rely=0.233, relwidth=0.981, relheight=0.469)

        self.style.configure('TFrame1.TLabelframe', font=('宋体',9))
        self.style.configure('TFrame1.TLabelframe.Label', font=('宋体',9))
        self.Frame1 = LabelFrame(self, text='', style='TFrame1.TLabelframe')
        self.Frame1.place(relx=0.01, rely=0., relwidth=0.981, relheight=0.219)

        self.style.configure('TCommand12.TButton', font=('宋体',22,'bold'))
        self.Command12 = Button(self.Frame3, text='取消', command=lambda: self.Command12_Cmd(root), style='TCommand12.TButton')
        self.Command12.place(relx=0.567, rely=0.198, relwidth=0.399, relheight=0.661)

        self.style.configure('TCommand13.TButton', font=('宋体',22,'bold'))
        self.Command13 = Button(self.Frame2, text='0', command=self.Command13_Cmd, style='TCommand13.TButton')
        self.Command13.place(relx=0.652, rely=0.533, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand10.TButton', font=('宋体',22,'bold'))
        self.Command10 = Button(self.Frame2, text='Del', command=self.Command10_Cmd, style='TCommand10.TButton')
        self.Command10.place(relx=0.815, rely=0.107, relwidth=0.144, relheight=0.787)

        self.style.configure('TCommand9.TButton', font=('宋体',22,'bold'))
        self.Command9 = Button(self.Frame2, text='9', command=self.Command9_Cmd, style='TCommand9.TButton')
        self.Command9.place(relx=0.499, rely=0.533, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand8.TButton', font=('宋体',22,'bold'))
        self.Command8 = Button(self.Frame2, text='8', command=self.Command8_Cmd, style='TCommand8.TButton')
        self.Command8.place(relx=0.346, rely=0.533, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand7.TButton', font=('宋体',22,'bold'))
        self.Command7 = Button(self.Frame2, text='7', command=self.Command7_Cmd, style='TCommand7.TButton')
        self.Command7.place(relx=0.194, rely=0.533, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand6.TButton', font=('宋体',22,'bold'))
        self.Command6 = Button(self.Frame2, text='6', command=self.Command6_Cmd, style='TCommand6.TButton')
        self.Command6.place(relx=0.041, rely=0.533, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand5.TButton', font=('宋体',22,'bold'))
        self.Command5 = Button(self.Frame2, text='5', command=self.Command5_Cmd, style='TCommand5.TButton')
        self.Command5.place(relx=0.652, rely=0.107, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand4.TButton', font=('宋体',22,'bold'))
        self.Command4 = Button(self.Frame2, text='4', command=self.Command4_Cmd, style='TCommand4.TButton')
        self.Command4.place(relx=0.499, rely=0.107, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand3.TButton', font=('宋体',22,'bold'))
        self.Command3 = Button(self.Frame2, text='3', command=self.Command3_Cmd, style='TCommand3.TButton')
        self.Command3.place(relx=0.346, rely=0.107, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand2.TButton', font=('宋体',22,'bold'))
        self.Command2 = Button(self.Frame2, text='2', command=self.Command2_Cmd, style='TCommand2.TButton')
        self.Command2.place(relx=0.194, rely=0.107, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand1.TButton', font=('宋体',22,'bold'))
        self.Command1 = Button(self.Frame2, text='1', command=self.Command1_Cmd, style='TCommand1.TButton')
        self.Command1.place(relx=0.041, rely=0.107, relwidth=0.102, relheight=0.356)

        self.style.configure('TCommand11.TButton', font=('宋体',22,'bold'))
        self.Command11 = Button(self.Frame3, text='确认', command=self.Command11_Cmd, style='TCommand11.TButton')
        self.Command11.place(relx=0.034, rely=0.198, relwidth=0.399, relheight=0.661)

        self.Text1Var = StringVar(value='')
        self.Text1 = Entry(self.Frame1, textvariable=self.Text1Var, font=('宋体',22,'bold'))
        self.Text1.place(relx=0.296, rely=0.305, relwidth=0.623, relheight=0.467)

        self.style.configure('TLabel1.TLabel', anchor='w', font=('宋体',22))
        self.Label1 = Label(self.Frame1, text='请输入密码', style='TLabel1.TLabel')
        self.Label1.place(relx=0.082, rely=0.381, relwidth=0.195, relheight=0.314)

strPwd = []
def UpdatePwd(self,strNum):
    global strPwd
    if len(strPwd)>=6:
        return
    else:
        strPwd.append(strNum)
    print(strNum)
    self.Text1Var.set("".join(strPwd))
    self.Text1.update()

class PageFour(Application_ui):
    # 这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self,parent,root):
        Application_ui.__init__(self,parent,root)
        self.root = root

    def Command12_Cmd(self,root, event=None):
        #TODO, Please finish the function here!
        root.show_frame(PageTwo)
        print('enter 取消')
        pass

    def Command13_Cmd(self, event=None):
        #TODO, Please finish the function here!
        funcname(self,'0')
        print('enter 0')
        pass

    def Command10_Cmd(self, event=None):
        #TODO, Please finish the function here!
        global strPwd
        if len(strPwd)>0:
            strPwd.pop()
            self.Text1Var.set("".join(strPwd))
            self.Text1.update() 
            print('enter DEL')
        pass

    def Command9_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'9')
        print('enter 9')
        pass

    def Command8_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'8')
        print('enter 8')
        pass

    def Command7_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'7')
        print('enter 7')
        pass

    def Command6_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'6')
        print('enter 6')
        pass

    def Command5_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'5')
        print('enter 5')
        pass

    def Command4_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'4')
        print('enter 4')
        pass

    def Command3_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'3')
        print('enter 3')
        pass

    def Command2_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'2')
        print('enter 2')
        pass

    def Command1_Cmd(self, event=None):
        #TODO, Please finish the function here!
        UpdatePwd(self,'1')
        print('enter 1')
        pass

    def Command11_Cmd(self, event=None):
        #TODO, Please finish the function here!
        # 退出输入界面
        # 
        print('enter 确认')
        pass
def ask_quit():
    if tkinter.messagebox.askyesno("提示！","是否退出程序?"):
        #线程杀死退出
        top.quit()


if __name__ == "__main__":
    top = Tk()
    top.protocol("WM_DELETE_WINDOW",ask_quit)
    Application(top).mainloop()



