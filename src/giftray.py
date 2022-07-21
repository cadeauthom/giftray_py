



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

    def _begin(self):
        self.showname           = "GifTray"
        self.name               = "giftray"
        message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): self._restart,
                       win32con.WM_DESTROY: self._destroy,
                       win32con.WM_COMMAND: self._command,
                       win32con.WM_USER+20 : self._notify,}
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
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, self.main_hicon, self.showname)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)

    def _show_menu(self):
        menu = win32gui.CreatePopupMenu()
        self.create_menu(menu, self.menu_options)
        #win32gui.SetMenuDefaultItem(menu, 1000, 0)

        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                self.hwnd,
                                None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def create_menu(self, menu, menu_options):
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = self.prep_menu_icon(option_icon)

            if option_id in self.menu_actions_by_id:
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                self.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def _popup(self, title, msg):
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, \
                         (self.hwnd, 0, win32gui.NIF_INFO,  win32con.WM_USER+20,\
                          self.main_hicon, "",msg,400,title, win32gui.NIIF_NOSOUND))

    def _notify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONDBLCLK:
            pass
            #self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
        elif lparam==win32con.WM_RBUTTONUP:
            self._show_menu()
        elif lparam==win32con.WM_LBUTTONUP:
            pass
        return True

    def _destroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0) # Terminate the app.

    def _command(self, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        self.execute_menu_option(id)

    def _restart(self, hwnd, msg, wparam, lparam):
        return True

    def wait(self):
        win32gui.PumpMessages()

if __name__ == '__main__':
    #import itertools, glob
    a=MainClass()
    a.wait()

    #ball=WindowsBalloonTip.BalloonTip("my test","this is my test", ico="../dist/giftray/icons/black/giftray-0.ico",taskbarname="GifTray-Tip",time=20)
    #ball.popup()
    #  time.sleep(20)
