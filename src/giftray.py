

import os
import sys
import inspect
#import time
#import win32api         # package pywin32
import win32con
#import keyboard
import configparser
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui
import win32gui_struct
import logging
import importlib

import icon
from feature import feature

def str_to_class(module,feat):
    return getattr(sys.modules[module], feat)

#keyboard.add_hotkey('ctrl + shift + z', print, args =('Hotkey', 'Detected'))
class MainClass(object):
    def __init__(self):
        self._begin()
        self._reset()
        self._loadmodules(['wsl','windows'])
        self._readconf()
        self._useconf()

    def _begin(self):
        self.showname           = "GifTray"
        self.name               = "giftray"
        logging.basicConfig(filename="giftray.log",level=0,format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logging.info("Initialising main class")
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
          #for i in self.avail:
          #  if hasattr(i, "destroy"): i.destroy(i)
          del self.avail
        #self.avail              = dict()
        self.avail              = []
        if hasattr(self, "error"):
          del self.error
        self.error              = dict()
        if hasattr(self, "install"):
          del self.install
        self.install            = dict()
        if hasattr(self, "menu"):
          del self.menu
        self.menu               = []
        self.conf               = os.getenv('USERPROFILE')+'/'+self.name+'/'+self.name+".conf"
        if hasattr(self, "icos"):
          del self.icos
        self.icos               = []
        self.conf_colormainicon = "blue"
        self.conf_coloricons    = "blue"
        self.conf_ico_default   = "default_default"
        self.conf_ico_empty     = "default_empty"
        self.conf_icoPath       = ""
        self.iconPath           = ""

    def _loadmodules(self,mods):
        for m in mods:
            try :
                tmp = importlib.import_module(m)
            except:
                logging.error("Module '" +m+ "' does not exist")
                continue
            for fct, obj in inspect.getmembers(tmp):
                if not (inspect.isclass(obj) and fct != 'feature'):
                    continue
                full = m+"_"+fct
                if not "_action" in (dir(obj)):
                    logging.error("Feature '" +full+ "' does not have '_action' defined")
                self.avail.append(full)
                #self.avail[full]            = dict()
                #self.avail[full]["fct"]     = fct
                #self.avail[full]["module"]  = m
                #self.avail[full]["feature"] = obj

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
        logging.info(config.sections())
        #config.write()
        self._conf2data(config)
        return 0

    def _conf2data(self,conf):
        for i in conf.sections():
            if i.casefold() == 'GENERAL'.casefold():
                for k in conf[i]:
                    if k.casefold() == 'ColorMainIcon'.casefold():
                        self.conf_colormainicon = str(conf[i][k])
                    elif k.casefold() == 'ColorIcons'.casefold():
                        self.conf_coloricons = str(conf[i][k])
                    else :
                        logging.error(i+"->"+k+"not supported")
            else:
                if "function" in conf[i]:
                    fct = conf[i]["function"].casefold()
                else:
                    logging.error("'function' not defined in '"+i+"'")
                if fct.count('_') != 1:
                    logging.error("'"+fct+"' does not contain exactly 1 '_' in '"+i+"'")
                    continue
                split_i = fct.split("_")
                module = split_i[0]
                feat = split_i[1]
                if  not module in sys.modules.keys():
                    logging.error("Module '"+module+"' not loaded from '"+i+"'")
                    continue
                if not fct in self.avail:
                    logging.error("'"+feat+"' not defined in module '" +module+"' from '"+i+"'")
                    continue
                new_class = str_to_class(module,feat)(i,conf[i],self)
                if not new_class.is_ok():
                    self.error[new_class.print()] = new_class.print_error(sep=",",prefix="")
                if new_class.is_in_menu():
                    self.menu.append(new_class.print())
                self.install[new_class.print()]=new_class

    def _useconf(self):
        self.iconPath=icon.ValidateIconPath( path    = self.conf_icoPath,\
                                             color   = self.conf_colormainicon, \
                                             project = self.name)
        self.main_hicon=icon.GetIcon(self.iconPath, ico=self.name+"-0.ico")
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, self.main_hicon, self.name)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)

    def _show_menu(self):
        menu = win32gui.CreatePopupMenu()
        #self._create_menu(menu, self.menu_options)
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

    def _create_menu(self, menu, menu_options):
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
        if True:
            print ("----- avail ------")
            print (self.avail)
            print ("----- error ------")
            print (self.error)
            print ("----- install ------")
            print (self.install)
            print ("----- menu ------")
            print (self.menu)
        win32gui.PumpMessages()

if __name__ == '__main__':
    #import itertools, glob
    a=MainClass()
    logging.info("Entering wait state")
    a.wait()
    logging.info("Exiting")
    #ball=WindowsBalloonTip.BalloonTip("my test","this is my test", ico="../dist/giftray/icons/black/giftray-0.ico",taskbarname="GifTray-Tip",time=20)
    #ball.popup()
    #  time.sleep(20)
