



import os
import sys
#import time
import win32api         # package pywin32
import win32con
import win32gui_struct
import keyboard
import configparser

try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

def ValidateIconPath(path="",color="black",project=""):
    if path:
        path = os.path.abspath(os.path.join(path,color))
        if os.path.isdir(path):
            return path
    path = os.path.abspath(os.path.join( sys.path[0], color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "..\\"+color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "icons\\"+color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "..\\icons\\"+color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "..\\dist\\"+project+"\\icons\\"+color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "..\\build\\"+project+"\\icons\\"+color))
    if os.path.isdir(path):
        return path
    return ""

def GetIcon(path,ico="default_default.ico"):
    last_try=False
    if ico=="default_default.ico":
        last_try=True
    if not ico:
        ico="default_default.ico"
    iconPathName = os.path.abspath(os.path.join( path, ico ))
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    if os.path.isfile(iconPathName):
        try:
            return win32gui.LoadImage(0, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
            pass
    if not last_try:
        return GetIcon(path)
    return win32gui.LoadIcon(0, win32con.IDI_APPLICATION)


#keyboard.add_hotkey('ctrl + shift + z', print, args =('Hotkey', 'Detected')) 
class MainClass(object):
    def __init__(self):
        self._begin()
        self._reset()
        self._readconf()
        self._useconf()
        self._PopUp("f","a")

    def _begin(self):
        self.showname           = "GifTray"
        self.name               = "giftray"
        message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
                # win32con.WM_CLOSE: self.onClose
        }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32gui.GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow( classAtom, self.showname+"TaskBar", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, win32gui.LoadIcon(0, win32con.IDI_APPLICATION), self.name)
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

    def _reset(self):
        if hasattr(self, "avail"):
          for i in self.avail:
            if hasattr(i, "destroy"): i.destroy(i)
          del self.avail
        self.avail              = []
        if hasattr(self, "error"):
          del self.error
        self.error              = []
        if hasattr(self, "install"):
          del self.install
        self.install            = []
        self.conf               = os.getenv('USERPROFILE')+'/'+self.name+'/'+self.name+".conf"
        if hasattr(self, "icos"):
          del self.icos
        self.icos               = []
        self.conf_color         = "blue"
        self.conf_ico_default   = "default_default"
        self.conf_ico_empty     = "default_empty"
        self.conf_icoPath       = ""
        self.iconPath           = ""

    def _readconf(self):
        config = configparser.ConfigParser()
        if os.path.isfile(self.conf) :
            config.read(self.conf)
        elif os.path.isfile(os.getcwd()+'/'+self.name+".conf") :
            config.read(os.getcwd()+'/'+self.name+".conf")
        elif os.path.isfile(os.getcwd()+'/conf/'+self.name+".conf") :
            config.read(os.getcwd()+'/conf/'+self.name+".conf")
        elif os.path.isfile(os.getcwd()+'/../../conf/'+self.name+'.conf') :
            config.read(os.getcwd()+'/../../conf/'+self.name+'.conf')
        else :
            return 1
        print (config.sections())
        #config.write()
        return 0

    def _useconf(self):
        self.iconPath=ValidateIconPath( path    = self.conf_icoPath,\
                                        color   = self.conf_color, \
                                        project = self.name)
        self.main_hicon=GetIcon(self.iconPath, ico=self.name+"-0.ico")
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, self.main_hicon, self.name)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)

    def _PopUp(self, title, msg):
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, \
                         (self.hwnd, 0, win32gui.NIF_INFO,  win32con.WM_USER+20,\
                          self.main_hicon, "",msg,400,title, win32gui.NIIF_NOSOUND))

    def onClose(self, hwnd): #to be called from thread as a method of the class instance
        win32gui.DestroyWindow(hwnd)
        classAtom = win32gui.UnregisterClass(classAtom, hinst)
        return True

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0) # Terminate the app.

if __name__ == '__main__':
    #import itertools, glob
    MainClass()

    #ball=WindowsBalloonTip.BalloonTip("my test","this is my test", ico="../dist/giftray/icons/black/giftray-0.ico",taskbarname="GifTray-Tip",time=20)
    #ball.popup()
    #  time.sleep(20)
