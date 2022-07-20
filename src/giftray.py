

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
import feature

def str_to_class(module,feat):
    return getattr(sys.modules[module], feat)

#keyboard.add_hotkey('ctrl + shift + z', print, args =('Hotkey', 'Detected'))
class MainClass(object):
    def __init__(self):
        self._begin()
        self._reset()
        self._load_modules(['wsl','windows'])
        self._read_conf()
        self._create_notify()

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
          pass
        else:
            self.avail = []
        if hasattr(self, "error"):
          self.error.clear()
        else:
            self.error = dict()
        if hasattr(self, "install"):
          self.install.clear()
        else:
            self.install = dict()
        if hasattr(self, "menu"):
          self.menu.clear()
        else:
            self.menu = []
        self.conf               = os.getenv('USERPROFILE')+'/'+self.name+'/'+self.name+".conf"
        if hasattr(self, "icos"):
          self.icos.clear()
        else:
            self.icos = []
        self.conf_colormainicon = "blue"
        self.conf_coloricons    = "blue"
        self.conf_ico_default   = "default_default"
        self.conf_ico_empty     = "default_empty"
        self.conf_icoPath       = ""
        self.iconPath           = ""

    def _load_modules(self,mods):
        for m in mods:
            try :
                tmp = importlib.import_module(m)
            except Exception as e:
                e_str = str(e)
                print("Module '" +m+ "' does not exist: "+e_str)
                logging.error("Module '" +m+ "' does not exist: "+e_str)
                continue
            for fct, obj in inspect.getmembers(tmp):
                if not (inspect.isclass(obj) and fct != 'main'):
                    continue
                full = m+"."+fct
                if m != obj.__module__:
                    logging.error("Issue while loading '" +full+ "': mismatch modules name: '"+m+"'!='"+obj.__module__+"'")
                    continue
                if fct != obj.__name__:
                    logging.error("Issue while loading '" +full+ "': mismatch feature name: '"+fct+"'!='"+obj.__name__+"'")
                    continue
                if not "_custom_action" in (dir(obj)):
                    logging.error("Feature '" +full+ "' does not have '_custom_action' defined")
                self.avail.append(full)

    def _read_conf(self):
        #Find and read config file
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
        #Load config to variables
        for section in config.sections():
            if section.casefold() == 'GENERAL'.casefold():
                for k in config[section]:
                    if k.casefold() == 'ColorMainIcon'.casefold():
                        self.conf_colormainicon = str(config[section][k])
                    elif k.casefold() == 'ColorIcons'.casefold():
                        self.conf_coloricons = str(config[section][k])
                    else :
                        logging.error(section+"->"+k+"not supported")
            else:
                if "function" in config[section]:
                    fct = config[section]["function"].casefold()
                else:
                    logging.error("'function' not defined in '"+section+"'")
                if fct.count('.') != 1:
                    logging.error("'"+fct+"' does not contain exactly 1 '.' in '"+section+"'")
                    continue
                split_section = fct.split(".")
                module = split_section[0]
                feat = split_section[1]
                if  not module in sys.modules.keys():
                    logging.error("Module '"+module+"' not loaded from '"+section+"'")
                    continue
                print (fct)
                if not fct in self.avail:
                    logging.error("'"+feat+"' not defined in module '" +module+"' from '"+section+"'")
                    continue
                new_class = str_to_class(module,feat)(section,config[section],self)
                if not new_class.is_ok():
                    self.error[new_class.print()] = new_class.print_error(sep=",",prefix="")
                if new_class.is_in_menu():
                    self.menu.append(new_class.print())
                self.install[new_class.print()]=new_class
        return 0

    def _create_notify(self):
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

    def popup(self, title, msg):
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
        if False:
            print ("----- avail ------")
            print (self.avail)
            print ("----- error ------")
            print (self.error)
            print ("----- install ------")
            print (self.install)
            for i in self.install:
                print (i)
                out = self.install[i].action()
                if out:
                    self.popup(i,out)
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
