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
import functools

from . import _general
from . import _icon
#from . import feature
#from . import _template
from . import _wsl
from . import _windows

'''
#when (function), development is planned, not done yet
def __init__(self):
    obviously called
def __del__(self):
    obviously called
def _define_tray(self):
    define tray and click events
    by __init__
def _reset(self):
    called to reset variables
    by __init__, __del__ (and by reload)
def _load_modules(self,mods):
    check/load modules
    by __init__
def _read_conf(self):
    called to read conf and build all variables
    by __init__ (and by reload)
def _set_icon(self):
    define main info of icons
    by _read_conf
def _create_menu(self):
    build the menu of the tray gui windows
    by _start
def _print_conf(self):
    return configuration in ini format
    (by save_conf, show_conf windows ?)
        def _run_thread(self,args):
def _run_thread(self,args):
    thread to run called action
    by _run_action
def _run_action(self,action):
    start run thread for called action
    by _ahk_thread (and click on menu)
def _tray_activation(self, reason):
    catch click on menu
    by __init__
def _debug_print(self):
    print some internal variables
    by run (with hack)
def _ahk_thread(self):
    threads to wait ahk/menu, started in main function
    set in _reset
    by run
def _flush_thread(self):
    thread to flush logs
    by run
def _about(self):
    action for about TOSA
    by _read_conf
def _reload(self):
    action for reload
    by _read_conf
def _start(self):
    start threads and any tools that can be reloaded
    by run & _reload
def run(self):
    main function
    print debug info
    should desappear
'''

class program(object):
    def __init__(self):
        self.stop_process       = False
        def signal_handler(signum, frame):
            self.__del__()
        # Register our signal handler with `SIGINT`(CTRL + C)
        signal.signal(signal.SIGINT, signal_handler)
        #signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.showname           = "GifTray"
        self.name               = "giftray"
        self.modules            = ['wsl','windows','template']
        #self.modules           = ['template'] # to debug with empty application
        logging.basicConfig     ( filename=self.name+".log",
                                  level=0,
                                  format='%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')
        self.logger             = logging.getLogger(__name__)
        self._define_tray       ()
        self._load_modules      ( self.modules )
        self._reload            ()
        self.logger.info        ("Entering wait state")
        th = _general.KThread(target=self._flush_thread)
        th.start()
        timer = PyQt6.QtCore.QTimer()
        timer.start(500)  # You may change this if you wish.
        timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
        if False: self._debug_print()
        self.app.exec()
        if th.is_alive():
            self.logger.debug('Kill flusher')
            th.kill()
        return

    def __del__(self):
        self.app.quit()
        self.stop_process = True
        self._reset()
        self.logger.info("Exiting")

    def _define_tray(self):
        # Define app
        self.app  = PyQt6.QtWidgets.QApplication([])
        self.app.setQuitOnLastWindowClosed ( False )
        #self.win_handler        = PyQt6.QtWidgets.QWidget()
        # Define tray
        self.tray = PyQt6.QtWidgets.QSystemTrayIcon(
                        PyQt6.QtWidgets.QWidget().style().standardIcon( #or self.win_handler
                            PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion))
        self.tray.setToolTip ( str(self.showname) )
        self.tray.setVisible ( True )
        self.tray.show()
        self.tray.activated.connect( self._tray_activation )
        return

    def _reset(self):
        if hasattr(self, "tray_menu"):
             self.tray_menu.clear()
        else:
            self.tray_menu = PyQt6.QtWidgets.QMenu()
        if hasattr(self, "ahk_thread"):
            if self.ahk_thread.is_alive():
                #self.ahk_thread.kill()
                ctypes.windll.user32.PostThreadMessageW(self.ahk_thread.native_id, win32con.WM_QUIT, 0, 0)
        self.ahk_thread         = _general.KThread(target=self._ahk_thread)
        if hasattr(self, "lock"):
            if self.lock.locked():
                self.lock.release()
        else:
            self.lock               = _general.Lock()
        if hasattr(self, "ahk_translator"):
            pass
        else:
            self.ahk_translator = _general.ahk()
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
        self.conf = os.getenv('USERPROFILE')+'/'+self.name+'/'+self.name+".conf"
        if hasattr(self, "icos"):
            self.icos.clear()
        else:
            self.icos = []
        #TODO: clean self.main_sicon, self.main_hicon in reset
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
        self.avail = []
        for m in mods:
            mod=self.name+'._'+m
            if not mod in sys.modules:
                print("Module '" +m+ "' not loaded")
                self.logger.error("Module '" +m+ "' not loaded")
                continue
            tmp = importlib.import_module(mod)
            for fct, obj in inspect.getmembers(tmp):
                if not (inspect.isclass(obj) and fct != 'main'):
                    continue
                full = m+"."+fct
                if mod != obj.__module__:
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
        elif os.path.isfile(os.getcwd()+'/../conf/'+self.name+'.conf') :
            self.conf=os.getcwd()+'/../conf/'+self.name+'.conf'
        elif os.path.isfile(os.getcwd()+'/../../conf/'+self.name+'.conf') :
            self.conf=os.getcwd()+'/../../conf/'+self.name+'.conf'
        else :
            self.main_error = "Fail to find configuration"
            self.logger.error(self.main_error)
            #return 1
        try:
            config.read(self.conf)
        except Exception as e:
            self.main_error = "Fail to read configuration (" + self.conf + "): " + str(e)
            self.logger.error(self.main_error)
            #return 1
        #Load GENERAL config to variables
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
                            self.logger.error('LogLevel->'+k+"not supported")
                    elif k.casefold() == 'Ico'.casefold():
                        self.conf_ico = str(config[section][k])
                    elif k.casefold() == 'IcoPath'.casefold():
                        self.conf_icoPath = str(config[section][k])
                    else :
                        self.logger.error(section+"->"+k+"not supported")

        #Get ico for Tray
        self._set_icon()

        #Load actions config to variables
        for section in config.sections():
            if section.casefold() != 'GENERAL'.casefold():
                for i in config[section]:
                    if "\n" in config[section][i]:
                        self.error[section] = "Indentation issue in '" + section +"'"
                        self.logger.error("Indentation issue in '" + section +"'")
                        continue
                if section in self.error: continue
                if "function" in config[section]:
                    fct = config[section]["function"].casefold()
                else:
                    self.logger.error("'function' not defined in '"+section+"'")
                if fct.count('.') != 1:
                    self.logger.error("'"+fct+"' does not contain exactly 1 '.' in '"+section+"'")
                    continue
                split_section = fct.split(".")
                module = split_section[0]
                mod = self.name+'._'+module
                feat = split_section[1]
                if not mod in sys.modules.keys():
                    self.error[section] = "Module '"+module+"' not loaded"
                    self.logger.error("Module '"+module+"' not loaded for '"+section+"'")
                    continue
                if not fct in self.avail:
                    self.error[section] = "'"+feat+"' not defined in module '" +module + "'"
                    self.logger.error("'"+feat+"' not defined in module '" +module+"' from '"+section+"'")
                    continue
                new_class = _general.str_to_class(mod,feat)(section,config[section],self)
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

        return 0

    def _set_icon(self):
        if self.conf_colormainicon:
            self.iconPath=_icon.ValidateIconPath(path    = self.conf_icoPath,
                                                color   = self.conf_colormainicon,
                                                project = self.name)
        else:
            self.iconPath=_icon.ValidateIconPath(path    = self.conf_icoPath,
                                                project = self.name)
        sicon = _icon.GetTrayIcon(color="blue",project=self.name)
        self.tray.setIcon(sicon)
        #time.sleep(3)
        if self.conf_ico:
            self.main_sicon, self.main_hicon, path_ico = _icon.GetIcon(self.iconPath, self, ico=self.conf_ico)
        else:
            self.main_sicon, self.main_hicon, path_ico = _icon.GetIcon(self.iconPath, self, ico=self.name+"-0.ico")
        if not path_ico or "default_default" in path_ico:
            self.main_sicon, self.main_hicon, path_ico = _icon.GetIcon(self.iconPath, self, ico=self.name+".ico")

        #Set ico to Tray
        self.tray.setIcon(self.main_sicon)

        #Save info of ico for conf
        d_path_ico = _icon.GetIcon(
                            _icon.ValidateIconPath(path = "", color   = self.conf_colormainicon, project = self.name),
                            self,
                            ico=self.name+"-0.ico")[2]
        if False:
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

        #Get ico path
        self.iconPath=_icon.ValidateIconPath(path    = self.conf_icoPath,
                                            color   = self.conf_coloricons,
                                            project = self.name)

    def _print_conf(self):
        #TODO: _print_conf: level for default, all, ?
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

    def _create_menu(self):
        # Define menu configured actions
        # loop on modules for main menu and for Not Clickable
        menu_not = PyQt6.QtWidgets.QMenu('Not clickable',self.tray_menu)
        for i in self.install:
            if i in self.error:
                # not filling here since not defined action are in error but not in install
                pass
            elif i in self.menu:
                act = PyQt6.QtGui.QAction(self.install[i].sicon,i,self.tray_menu)
                act.triggered.connect(functools.partial(self._run_action, i))
                self.tray_menu.addAction(act)
            else:
                act = PyQt6.QtGui.QAction(self.install[i].sicon,i,menu_not)
                act.setDisabled(True)
                menu_not.addAction(act)

        # loop on modules in error
        menu_err = PyQt6.QtWidgets.QMenu('In error',self.tray_menu)
        sicon_err, _, _ = _icon.GetIcon(self.iconPath, self, ico='default_empty.ico')
        for i in self.error:
            act=PyQt6.QtGui.QAction(sicon_err,i,menu_err)
            act.triggered.connect(functools.partial(self._error, i, self.error[i]))
            menu_err.addAction(act)

        self.tray_menu.addSeparator()
        menu_ina = PyQt6.QtWidgets.QMenu('Inactive',self.tray_menu)
        #TODO find not use modules
        if not menu_ina.isEmpty():
            self.tray_menu.addMenu(menu_ina)
        if not menu_not.isEmpty():
            self.tray_menu.addMenu(menu_not)
        if not menu_err.isEmpty():
            self.tray_menu.addMenu(menu_err)

        if self.main_error:
            act = PyQt6.QtGui.QAction(self.showname + " Error",self.tray_menu)
            act.triggered.connect(functools.partial(self._error, self.showname, self.main_error))
            self.tray_menu.addAction(act)


        self.tray_menu.addSeparator()

        # Define menu default actions
        #ToDo generator Gui
        #ToDo conf Gui
        #ToDo about Gui
        #ToDo update link
        sicon, hicon, picon = _icon.GetIcon(self.iconPath, self, ico='default_generator.ico')
        act=PyQt6.QtGui.QAction('Generate HotKey',self.tray_menu)
        if picon:
            act.setIcon(sicon)
        act.setDisabled(True)
        #act.setStatusTip('not developed')
        #act.setShortcut('Ctrl+R')
        self.tray_menu.addAction(act)
        sicon, hicon, picon = _icon.GetIcon(self.iconPath, self, ico='default_showconf.ico')
        act=PyQt6.QtGui.QAction('Show current configuration',self.tray_menu)
        if picon:
            act.setIcon(sicon)
        act.setDisabled(True)
        self.tray_menu.addAction(act)
        sicon, hicon, picon = _icon.GetIcon(self.iconPath, self, ico='default_about.ico')
        act=PyQt6.QtGui.QAction('About '+self.showname,self.tray_menu)
        if picon:
            act.setIcon(sicon)
        act.triggered.connect(self._about)
        self.tray_menu.addAction(act)
        sicon, hicon, picon = _icon.GetIcon(self.iconPath, self, ico='default_reload.ico')
        act=PyQt6.QtGui.QAction('Reload '+self.showname,self.tray_menu)
        if picon:
            act.setIcon(sicon)
        act.triggered.connect(self._reload)
        self.tray_menu.addAction(act)
        self.tray_menu.addSeparator()
        sicon, hicon, picon = _icon.GetIcon(self.iconPath, self, ico='default_exit.ico')
        act=PyQt6.QtGui.QAction('Exit '+self.showname,self.tray_menu)
        if picon:
            act.setIcon(sicon)
        act.triggered.connect(self.__del__)
        self.tray_menu.addAction(act)

        self.tray.setContextMenu(self.tray_menu)
        return

    def _tray_activation(self,reason):
        if reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            pass
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.Context:
            self.tray_menu.show()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick:
            self._about()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.MiddleClick:
            self.__del__()
        return

    def _run_thread(self,args):
        if self.lock.acquire(timeout=1):
            action=self.install[args]
            start_time = datetime.datetime.now()
            show = action.show+start_time.strftime(" [%H%M%S]")
            self.logger.debug('Run '+show)
            th = _general.KThread(target=action.run)
            th.start()
            th.join(10)
            duration = datetime.datetime.now() - start_time
            if th.is_alive():
                self.logger.debug('Kill '+show +' after '+str(duration.seconds)+' sec')
                th.kill()
            else:
                self.logger.debug(show+ ' ran in '+str(duration.seconds)+' sec')
            #few seconds before releasing lock
            #TODO: releasing lock time in configuration
            time.sleep(3)
            self.logger.debug('Release lock')
            if self.lock.locked(): self.lock.release()
        return

    def _run_action(self,feature):
        if self.lock.locked():
            self.logger.debug('Lock locked for ' + self.install[feature].show)
            return
        a=_general.KThread(target=self._run_thread,args=[feature])
        a.start()
        return

    def _debug_print(self):
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

    def _ahk_thread(self):
        self.logger.info("Starting ahk thread")
        for ahk in self.ahk:
            if (ctypes.windll.user32.RegisterHotKey(None, self.nb_hotkey+1, self.install[self.ahk[ahk]].hhk["mod"] , self.install[self.ahk[ahk]].hhk["key"])):
                self.nb_hotkey += 1
                self.logger.debug("register "+str(ahk))
            else:
                self.install[self.ahk[ahk]].error.append("Fail to register Hotkey ("+ahk+")")
                self.error[self.ahk[ahk]]=self.install[self.ahk[ahk]].print_error(sep=",",prefix="")
                self.logger.err("fail to register"+str(ahk))
        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                ahk = self.ahk_translator.hhk2ahk({ "mod" : msg.lParam & 0b1111111111111111,
                                     "key" : msg.lParam >> 16})
                if ahk in self.ahk:
                    self._run_action(self.ahk[ahk])
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        self.logger.info("Ending ahk thread")
        return

    def _flush_thread(self):
        logger = logging.getLogger()
        while True:
            logger.handlers[0].flush()
            for i in range(10): time.sleep(1)
        return

    def _start(self):
        self._create_menu()
        self.ahk_thread.start()
        return

    def _about(self):
        return

    def _error(self,name,error):
        text = '<h3>'+name+'</h3>'

        info = '<ul>'
        l=0
        for e in error.split(', '):
            l = max(l,len(e))
            info += '<li>' + e + '</li>'
        info += '</ul>'
        l = 45+min(l,80)
        info += '<p>'
        for i in range(l): info += '&nbsp;'
        info += '</p>'
        box = PyQt6.QtWidgets.QMessageBox()
        box.setWindowTitle(self.showname)
        box.setText(text)
        box.setInformativeText(info)
        #box.setStandardButtons(PyQt6.QtWidgets.Ok)
        p = self.main_sicon.pixmap(20)
        box.setIconPixmap(p)
        box.exec()
        return

    def _reload(self):
        self._reset()
        self._read_conf()
        self._start()
        return

if __name__ == '__main__':
    #import itertools, glob
    a=MainClass()

    '''
    import threading
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
           pass
        else:
            ctypes.windll.user32.PostThreadMessageW(t.native_id, win32con.WM_QUIT, 0, 0)
    '''
