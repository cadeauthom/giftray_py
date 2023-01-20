import os
import io
import sys
import posixpath
import signal
import inspect
import time
import datetime
import win32api         # package pywin32
import win32con
import win32process
import configparser
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui
# import win32gui_struct
import logging
import importlib
import ctypes, ctypes.wintypes
import PyQt6.QtWidgets, PyQt6.QtGui
import notifypy

import general
import icon
import feature

'''
when (function), it is planned, not done yet
def __init__(self):
    obviously called
def __del__(self):
    obviously called_
def _reset(self):
    called to reset variables
    by __init__ (and by reload)
def _load_modules(self,mods):
    check/load modules
    by __init__
def _read_conf(self):
    called to read conf and build all variables
    by __init__ (and by reload)
            def _show_menu(self):
                show the main tray gui (while clickink)
                by _notify
            def _create_menu(self, menu, menu_options):
                build the menu of the tray gui windows
                by _show_menu
def popup(self, title, msg):
    popup message when action is run
    (by run)
def hhk2ahk(self,hhk):
def ahk2hhk(self,ahk):
    translate hk from/to lisible/tool
    by feature module
def _print_conf(self):
    return configuration in ini format
    (by save_conf, show_conf windows ?)
def _run_action(self,action):
    run called action
    by _ahk_thread (and click on menu)
def _menu_thread(self):
def _ahk_thread(self):
    threads to wait ahk/menu, started in main function
    by _reset
def run(self):
    main function
    print debug info
    should desappear
'''

class MainClass(object):
    def __init__(self):
        self.showname           = "GifTray"
        self.name               = "giftray"
        self.app                = PyQt6.QtWidgets.QApplication([])
        self.app.setQuitOnLastWindowClosed (
                                  False )
        #self.win_handler        = PyQt6.QtWidgets.QWidget()
        self.tray               = PyQt6.QtWidgets.QSystemTrayIcon()
        self.tray.setIcon       ( PyQt6.QtWidgets.QWidget().style().standardIcon( #or self.win_handler
                                    PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion))
        self.tray.setToolTip    ( "GifTray" )
        self.tray.setVisible    ( True )
        #self.tray.activated.connect( self.__del__)
        #self.tray.showMessage("1","2",self.win_handler.style().standardIcon(
        #                            PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion))
        self.stop_process       = False
        logging.basicConfig     ( filename=self.name+".log",
                                  level=0,
                                  format='%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')
        self.logger             = logging.getLogger(__name__)
        self._reset             ()
        self._load_modules      ( ['wsl','windows'] )
        self._read_conf         ()

    def __del__(self):
        self.stop_process = True
        self._reset()

    def _reset(self):
        if hasattr(self, "ahk_thread"):
            if self.ahk_thread.is_alive():
                #self.ahk_thread.kill()
                ctypes.windll.user32.PostThreadMessageW(self.ahk_thread.native_id, win32con.WM_QUIT, 0, 0)
        self.ahk_thread         = general.KThread(target=self._ahk_thread)
        if hasattr(self, "menu_thread"):
            if self.menu_thread.is_alive():
                #self.menu_thread.kill()
                ctypes.windll.user32.PostThreadMessageW(self.menu_thread.native_id, win32con.WM_QUIT, 0, 0)
        self.menu_thread        = general.KThread(target=self._menu_thread)
        if hasattr(self, "lock"):
            if self.lock.locked():
                self.lock.release()
        else:
            self.lock               = general.Lock()
        if hasattr(self, "ahk_mods"):
            pass
        else:
            self.ahk_mods = {}
            self.ahk_keys = {}
            for item, value in vars(win32con).items():
                if item.startswith("MOD_"):
                    self.ahk_mods[item] = value
                    self.ahk_mods[value] = item
                elif item.startswith("VK_"):
                    self.ahk_keys[item] = value
                    self.ahk_keys[value] = item
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
        if hasattr(self, "ahk"):
            self.ahk.clear()
        else:
            self.ahk = dict()
        if hasattr(self, "hhk"):
            self.hhk.clear()
        else:
            self.hhk = []
        self.conf               = os.getenv('USERPROFILE')+'/'+self.name+'/'+self.name+".conf"
        if hasattr(self, "icos"):
            self.icos.clear()
        else:
            self.icos = []
        #TODO: clean self.main_sicon, self.main_hicon
        if hasattr(self, "nb_hotkey"):
            for i in range(self.nb_hotkey):
                ctypes.windll.user32.UnregisterHotKey(None, i)
        self.nb_hotkey = 0
        self.conf_colormainicon = ""
        self.conf_coloricons    = ""
        self.conf_loglevel      = "WARNING"
        self.conf_ico_default   = "default_default"
        self.conf_ico_empty     = "default_empty"
        self.conf_ico           = ""
        self.conf_icoPath       = ""
        self.iconPath           = ""
        self.main_error         = ""

    def _load_modules(self,mods):
        for m in mods:
            try :
                tmp = importlib.import_module(m)
            except Exception as e:
                e_str = str(e)
                print("Module '" +m+ "' not loaded: "+e_str)
                self.logger.error("Module '" +m+ "' not loaded: "+e_str)
                continue
            for fct, obj in inspect.getmembers(tmp):
                if not (inspect.isclass(obj) and fct != 'main'):
                    continue
                full = m+"."+fct
                if m != obj.__module__:
                    self.logger.error("Issue while loading '" +full+ "': mismatch modules name: '"+m+"'!='"+obj.__module__+"'")
                    continue
                if fct != obj.__name__:
                    self.logger.error("Issue while loading '" +full+ "': mismatch feature name: '"+fct+"'!='"+obj.__name__+"'")
                    continue
                if not "_custom_run" in (dir(obj)):
                    self.logger.error("Feature '" +full+ "' does not have '_custom_run' defined")
                self.avail.append(full)

    def _read_conf(self):
        #Find and read config file
        config = configparser.ConfigParser()
        if os.path.isfile(self.conf) :
            pass
        elif os.path.isfile(os.getcwd()+'/'+self.name+".conf") :
            self.conf=os.getcwd()+'/'+self.name+".conf"
        elif os.path.isfile(os.getcwd()+'/conf/'+self.name+".conf") :
            self.conf=os.getcwd()+'/conf/'+self.name+".conf"
        elif os.path.isfile(os.getcwd()+'/../../conf/'+self.name+'.conf') :
            self.conf=os.getcwd()+'/../../conf/'+self.name+'.conf'
        else :
            self.main_error = "Fail to find configuration"
            self.logger.error(self.main_error)
            return 1
        try:
            config.read(self.conf)
        except Exception as e:
            self.main_error = "Fail to read configuration (" + self.conf + "): " + str(e)
            self.logger.error(self.main_error)
            return 1
        #Load config to variables
        for section in config.sections():
            if section.casefold() == 'GENERAL'.casefold():
                for k in config[section]:
                    if k.casefold() == 'ColorMainIcon'.casefold():
                        self.conf_colormainicon = str(config[section][k])
                    elif k.casefold() == 'ColorIcons'.casefold():
                        self.conf_coloricons = str(config[section][k])
                    elif k.casefold() == 'LogLevel'.casefold():
                        LevelNamesMapping=logging.getLevelNamesMapping()
                        levelname=str(config[section][k]).upper()
                        if levelname in LevelNamesMapping:
                            self.conf_loglevel = levelname.casefold()
                            self.logger.setLevel(level=LevelNamesMapping[levelname])
                        else:
                            print("nop")
                    elif k.casefold() == 'Ico'.casefold():
                        self.conf_ico = str(config[section][k])
                    elif k.casefold() == 'IcoPath'.casefold():
                        self.conf_icoPath = str(config[section][k])
                    else :
                        self.logger.error(section+"->"+k+"not supported")
            else:
                if "function" in config[section]:
                    fct = config[section]["function"].casefold()
                else:
                    self.logger.error("'function' not defined in '"+section+"'")
                if fct.count('.') != 1:
                    self.logger.error("'"+fct+"' does not contain exactly 1 '.' in '"+section+"'")
                    continue
                split_section = fct.split(".")
                module = split_section[0]
                feat = split_section[1]
                if  not module in sys.modules.keys():
                    self.error[section] = "Module '"+module+"' not loaded"
                    self.logger.error("Module '"+module+"' not loaded for '"+section+"'")
                    continue
                if not fct in self.avail:
                    self.error[section] = feat+"' not defined in module '" +module
                    self.logger.error("'"+feat+"' not defined in module '" +module+"' from '"+section+"'")
                    continue
                new_class = general.str_to_class(module,feat)(section,config[section],self)
                ahk, hhk = new_class.get_hk()
                if len(ahk)>2 and "key" in hhk:
                    if ahk in self.ahk:
                        new_class.error.append("Duplicated ahk " + self.ahk[ahk])
                        self.logger.error("'"+ahk+"' set twice! '" +self.ahk[ahk]+"' / '"+new_class.show+"'")
                    else:
                        self.ahk[ahk] = new_class.show
                if not new_class.is_ok():
                    self.error[new_class.show] = new_class.print_error(sep=",",prefix="")
                self.install[new_class.show]=new_class
                if new_class.is_in_menu():
                    self.menu.append(new_class.show)

        self.iconPath=icon.ValidateIconPath(path = self.conf_icoPath,
                                            color   = self.conf_colormainicon,
                                            project = self.name)
        if self.conf_ico:
            self.main_sicon, self.main_hicon, path_ico = icon.GetIcon(self.iconPath, self, ico=self.conf_ico)
        else:
            self.main_sicon, self.main_hicon, path_ico = icon.GetIcon(self.iconPath, self, ico=self.name+"-0.ico")
        d_path_ico = icon.GetIcon(
                            icon.ValidateIconPath(path = "", color   = self.conf_colormainicon, project = self.name),
                            self,
                            ico=self.name+"-0.ico")[2]
        print(path_ico)
        print(d_path_ico)
        if not path_ico:
            self.conf_icoPath       = ""
            self.conf_ico           = ""
            self.conf_colormainicon = ""
        else:
            name_ico     = os.path.basename(path_ico)
            path_ico     = os.path.dirname(path_ico)
            col_ico      = os.path.basename(path_ico)
            path_ico     = os.path.dirname(path_ico)
            if not d_path_ico:
                if self.conf_colormainicon:
                    self.conf_icoPath = path_ico
                    self.conf_colormainicon = col_ico
                else:
                    self.conf_icoPath = posixpath.join(path_ico,col_ico)
                self.conf_ico = name_ico
            else:
                d_name_ico  = os.path.basename(d_path_ico)
                d_path_ico  = os.path.dirname(d_path_ico)
                d_col_ico   = os.path.basename(d_path_ico)
                d_path_ico  = os.path.dirname(d_path_ico)
                if (d_name_ico != name_ico):
                    self.conf_ico = name_ico
                if (d_path_ico != path_ico):
                    if self.conf_colormainicon:
                        self.conf_icoPath = path_ico
                        self.conf_colormainicon = col_ico
                    else:
                        self.conf_icoPath = posixpath.join(path_ico,col_ico)
                else:
                    self.conf_colormainicon = col_ico
        print("conf_colormainicon   = "+self.conf_colormainicon)
        print("conf_coloricons      = "+self.conf_coloricons)
        print("conf_icoPath         = "+self.conf_icoPath)
        print("conf_ico             = "+self.conf_ico)
        return 0

    # def _show_menu(self):
        # menu = win32gui.CreatePopupMenu()
        # #self._create_menu(menu, self.menu_options)
        # #win32gui.SetMenuDefaultItem(menu, 1000, 0)
        # pos = win32gui.GetCursorPos()
        # # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        # win32gui.SetForegroundWindow(self.hwnd)
        # win32gui.TrackPopupMenu(menu,
                                # win32con.TPM_LEFTALIGN,
                                # pos[0],
                                # pos[1],
                                # 0,
                                # self.hwnd,
                                # None)
        # win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        # return

    # def _create_menu(self, menu, menu_options):
        # for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            # if option_icon:
                # option_icon = self.prep_menu_icon(option_icon)

            # if option_id in self.menu_actions_by_id:
                # item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                # hbmpItem=option_icon,
                                                                # wID=option_id)
                # win32gui.InsertMenuItem(menu, 0, 1, item)
            # else:
                # submenu = win32gui.CreatePopupMenu()
                # self.create_menu(submenu, option_action)
                # item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                # hbmpItem=option_icon,
                                                                # hSubMenu=submenu)
                # win32gui.InsertMenuItem(menu, 0, 1, item)
        # return

    def popup(self, title, msg):
        def callback (hwnd, hwnds):
            _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
            if found_pid == pid:
                # if win32gui.GetWindowText(hwnd) == "QTrayIconMessageWindow":
                if win32gui.GetClassName(hwnd) == "Qt642TrayIconMessageWindowClass":
                    hwnds.append (hwnd)
            return True
        hwnds = []
        pid=win32process.GetCurrentProcessId()
        win32gui.EnumWindows (callback, hwnds)
        if not hwnds:
            return
        hwnd = hwnds[0]
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                                    (hwnd, 0, win32gui.NIF_INFO, win32con.WM_USER + 20,
                                      self.main_hicon, "Balloon Tooltip", msg, 200, title, win32gui.NIIF_NOSOUND))
        #(hwnd, id, win32gui.NIF_*, CallbackMessage, hicon, Tooltip text (opt), Balloon tooltip text (opt), Timeout (ms), title (opt),  win32gui.NIIF_*)
        return

    def hhk2ahk(self,hhk):
        ahk = ""
        if hhk["mod"] & self.ahk_mods["MOD_CONTROL"]:
            ahk += "Ctrl + "
        if hhk["mod"] & self.ahk_mods["MOD_WIN"]:
            ahk += "Win + "
        if hhk["mod"] & self.ahk_mods["MOD_SHIFT"]:
            ahk += "Shift + "
        if hhk["mod"] & self.ahk_mods["MOD_ALT"]:
            ahk += "Alt + "
        if hhk["key"] in self.ahk_keys:
            ahk += self.ahk_keys[hhk["key"]][3:]
        else:
            ahk += chr(hhk["key"]).lower()
        return ahk

    def ahk2hhk(self,ahk):
        hhk = {}
        nb_k=0
        nb_m=0
        hhk["mod"] = 0
        arr = ahk.upper()
        arr = arr.split("+")
        if len(arr)<2:
            return {"mod":0}, ahk, "Shortcut too short"+ahk+")"
        for i in range(len(arr)):
            mod = arr[i].strip()
            if mod in ['CTRL',"LCTRL","RCTRL","CONTROL","LCONTROL","RCONTROL"]:
                nb_m += 1
                hhk["mod"] |= self.ahk_mods["MOD_CONTROL"]
            elif mod in ['WIN','LWIN','RWIN','WINDOWS','LWINDOWS','RWINDOWS']:
                nb_m += 1
                hhk["mod"] |= self.ahk_mods["MOD_WIN"]
            elif mod in ['ALT','LALT','RALT']:
                nb_m += 1
                hhk["mod"] |= self.ahk_mods["MOD_ALT"]
            elif mod in ['SHIFT','LSHIFT','RSHIFT','MAJ','LMAJ','RMAJ']:
                hhk["mod"] |= self.ahk_mods["MOD_SHIFT"]
            elif "VK_"+mod in self.ahk_keys:
                hhk["key"] = self.ahk_keys["VK_"+mod]
                nb_k += 1
            elif len(mod)==1:
                k=win32api.VkKeyScan(mod[0].lower())
                k = k & 0xFF
                hhk["key"] = k
                nb_k += 1
            else :
                return {"mod":0}, ahk, "Shortcut not well defined ("+mod+" in "+ahk+")"
        if not 'key' in hhk:
            return {"mod":0}, ahk, "Shortcut without key ("+ahk+")"
        if mod == 0 :
            return {"mod":0}, ahk, "Shortcut without modifier ("+ahk+")"
        if nb_m == 0 :
            return {"mod":0}, ahk, "Shortcut with only Shift modifier ("+ahk+")"
        if nb_k > 1:
            return {"mod":0}, ahk, "Shortcut with several keys ("+ahk+")"
        ahk = self.hhk2ahk(hhk)
        return hhk, ahk, ""

    def _print_conf(self):
        #TODO: level for default, all, ?
        config = configparser.ConfigParser()
        config["GENERAL"] = { "ColorMainIcon" : self.conf_colormainicon,  #default "blue"
                              "ColorIcons"    : self.conf_coloricons   ,  #default "blue"
                              "LogLevel"      : self.conf_loglevel     }  #default "WARNING"
        for i in self.install:
            config[i]={ "function" : self.install[i].module+ "." + self.install[i].name}
            #mandatory options
            config[i]["ahk"]=self.install[i].ahk
            config[i]["menu"]=str(self.install[i].menu)
            #optional options
            path_ico     = self.install[i].used_ico
            if path_ico:
                name_ico     = os.path.basename(path_ico)
                path_ico     = os.path.dirname(path_ico)
                col_ico      = os.path.basename(path_ico)
                path_ico     = os.path.dirname(path_ico)
                main_path_ico= os.path.dirname(self.iconPath)
                main_col_ico = os.path.basename(self.iconPath)
                if (main_path_ico != path_ico):
                    config[i]["ico"] = self.install[i].used_ico
                else:
                    if (col_ico != main_col_ico):
                        config[i]["color"] = col_ico
                    if (name_ico != self.install[i].module+ "_" + self.install[i].name + ".ico"):
                        config[i]["ico"] = name_ico
            for opt in self.install[i].get_opt():
                config[i][opt]=str(getattr(self.install[i], opt))
        f = io.StringIO()
        config.write(f)
        out = f.getvalue()
        f.close()
        return out


    def _run_thread(self,args):
        if self.lock.acquire(timeout=1):
            action=self.install[self.ahk[args]]
            start_time = datetime.datetime.now()
            show = action.show+start_time.strftime(" [%H%M%S]")
            self.logger.debug('Run '+show)
            th = general.KThread(target=action.run)
            th.start()
            th.join(10)
            duration = datetime.datetime.now() - start_time
            if th.is_alive():
                self.logger.debug('Kill '+show +' after '+str(duration.seconds)+' sec')
                th.kill()
            else:
                self.logger.debug(show+ ' ended'+' after '+str(duration.seconds)+' sec')
            #few seconds before releasing lock
            #TODO: in configuration ?
            time.sleep(3)
            self.logger.debug('Release lock')
            self.lock.release()
        return

    def _run_action(self,ahk):
        if self.lock.locked():
            self.logger.debug('Lock locked for ' + self.install[self.ahk[ahk]].show)
            return
        a=general.KThread(target=self._run_thread,args=[ahk])
        a.start()
        return

    def _menu_click(self, reason):
        print("onTrayIconActivated:", reason)
        #if reason == QSystemTrayIcon.Trigger:
        #    self.disambiguateTimer.start(qApp.doubleClickInterval())
        if reason == PyQt6.QtWidgets.QSystemTrayIcon.DoubleClick:
            print ("Tray icon double clicked")
        return

    def _menu_thread(self):
        self.logger.info("Starting menu thread")
        if False:
            print ("----- avail ------")
            print (self.avail)
            print ("----- error ------")
            print (self.error)
            print ("----- install ------")
            print (self.install)
            #for i in self.install:
                #out = self.install[i].run()
                #if out:
                #    self.popup(i,out)
            print ("----- menu ------")
            print (self.menu)
            print ("----- ahk ------")
            print (self.nb_hotkey)
            print (self.ahk)
            print ("----- conf -----")
            print (self._print_conf())
        self.logger.info("Ending menu thread")
        return

    def _ahk_thread(self):
        self.logger.info("Starting ahk thread")
        for ahk in self.ahk:
            if (ctypes.windll.user32.RegisterHotKey(None, self.nb_hotkey+1, self.install[self.ahk[ahk]].hhk["mod"] , self.install[self.ahk[ahk]].hhk["key"])):
                self.nb_hotkey += 1
                self.logger.debug("register "+str(ahk))
            else:
                self.install[self.ahk[ahk]].error.append("Fail to register Hotkey ("+ahk+")")
                self.logger.err("fail to register"+str(ahk))
        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                ahk = self.hhk2ahk({ "mod" : msg.lParam & 0b1111111111111111,
                                     "key" : msg.lParam >> 16})
                if ahk in self.ahk:
                    #TODO : generic: name
                    self._run_action(ahk)
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        self.logger.info("Ending ahk thread")
        return

    def run(self):
        def signal_handler(signum, frame):
            self.__del__()
        # Register our signal handler with `SIGINT`(CTRL + C)
        signal.signal(signal.SIGINT, signal_handler)
        self.menu_thread.start()
        self.ahk_thread.start()
        while not self.stop_process:
            time.sleep(0.2)
        return


if __name__ == '__main__':
    #import itertools, glob
    a=MainClass()
    a.logger.info("Entering wait state")
    a.run()
    #a.logger.info("Exiting")
    #a.destroy()
    '''
    import threading
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
           pass
        else:
            ctypes.windll.user32.PostThreadMessageW(t.native_id, win32con.WM_QUIT, 0, 0)
    '''
