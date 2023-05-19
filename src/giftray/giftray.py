import os
import io
import sys
import posixpath
import signal
import inspect
import time
import datetime
import glob
import shutil
#import win32api         # package pywin32
import win32con
import configparser
try:
    import win32gui
except ImportError:
    import winxpgui as win32gui
# import win32gui_struct
import logging
import importlib
import ctypes, ctypes.wintypes
import PyQt6.QtWidgets, PyQt6.QtGui
import notifypy
import functools
import natsort

from . import _general
from . import _icon
from . import _feature
#from . import _template
from . import _wsl
from . import _windows

class giftray(object):
    def __init__(self):
        def signal_handler(signum, frame):
            self.__del__()
        # Register our signal handler with `SIGINT`(CTRL + C)
        signal.signal(signal.SIGINT, signal_handler)
        self.showname           = 'GifTray'
        self.name               = 'giftray'
        self.generalsectionword = 'General'
        self.generalopt         = self.showname+' '+self.generalsectionword.title()
        self.nativeopt          = self.showname+' Native'
        self.modules            = ['wsl'.casefold(),'windows'.casefold()]
        #self.modules           = ['template'] # to debug with empty application
        self.userdir            = posixpath.join(os.getenv('USERPROFILE'), self.showname)
        filelog                 = posixpath.join(self.userdir, self.name+".log")
        if "\\python" in sys.executable:
            filelog             = self.name+".log"
            self.userdir        = posixpath.join(os.path.dirname(sys.executable),"conf")
        else:
            # executable not python; test if user dir exists
            #src = posixpath.join(os.getcwd(),"conf") # debug in python with revert previous 'if'
            src = posixpath.join(os.path.dirname(sys.executable),"conf")
            if not os.path.exists(self.userdir):
                #os.mkdir(self.userdir)
                shutil.copytree(src,self.userdir)
            else:
                for file in glob.glob(os.path.join(self.userdir,'*.example')):
                    os.remove(file)
                for file in glob.glob(os.path.join(src,'*.example')):
                    shutil.copy(file, self.userdir)
        logging.basicConfig     ( filename=filelog,
                                  level=0,
                                  encoding='utf-8',
                                  format='%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')
        self.logger             = logging.getLogger(__name__)
        # Define app
        self.app  = PyQt6.QtWidgets.QApplication([])
        self.app.setStyle('Fusion')
        self.app.setQuitOnLastWindowClosed ( False )
        #self.win_handler        = PyQt6.QtWidgets.QWidget()
        # Define tray
        self.tray = PyQt6.QtWidgets.QSystemTrayIcon(
                        PyQt6.QtWidgets.QWidget().style().standardIcon( #or self.win_handler
                            PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion))
        self.tray.setToolTip    ( str(self.showname) )
        self.tray.setVisible    ( True )
        self.tray.show          ()
        self.tray.activated.connect( self._ConnectorTray )
        self.avail              = []
        self.avail_modules      = dict()
        self.images             = _icon.svgIcons(self)
        for m in self.modules:
            mod=self.name+'._'+m
            if not mod in sys.modules:
                self.logger.error("Module '" +m+ "' not loaded")
                continue
            tmp = importlib.import_module(mod)
            for fct, obj in inspect.getmembers(tmp):
                if not (inspect.isclass(obj) and fct != 'main'):
                    continue
                if (fct == "general" ):
                    self.avail_modules[m] = _general.Str2Class(mod,fct)(self,m)
                    continue
                full = m+"."+fct
                if mod != obj.__module__:
                    self.logger.error("Issue while loading '" +full+ "': mismatch modules name: '"+m+"'!='"+obj.__module__+"'")
                    continue
                if fct != obj.__name__:
                    self.logger.error("Issue while loading '" +full+ "': mismatch feature name: '"+fct+"'!='"+obj.__name__+"'")
                    continue
                if not "_Run" in (dir(obj)):
                    self.logger.error("Feature '" +full+ "' does not have '_custom_run' defined")
                    continue
                self.avail.append(full)
            if not m in self.avail_modules:
                self.avail_modules[m] = _feature.general(self,m)
        self._Restart            ()
        self.logger.info        ("Entering wait state")
        th = _general.KThread(target=self._Thread4Flush)
        th.start()
        timer = PyQt6.QtCore.QTimer()
        timer.start(500)  # You may change this if you wish.
        timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
        self.app.exec()
        if th.is_alive():
            self.logger.debug('Kill flusher')
            th.kill()
        return

    def __del__(self):
        self._ResetVar()
        self.app.quit()
        self.logger.info("Exiting")

    def _ResetVar(self):
        if hasattr(self, "avail_modules"):
            for i in self.avail_modules:
                self.avail_modules[i].Clean()
        if hasattr(self, "tray_menu"):
             self.tray_menu.clear()
        else:
            self.tray_menu = PyQt6.QtWidgets.QMenu()
            self.tray_menu.setToolTipsVisible(True)
        if hasattr(self, "ahk_thread"):
            if self.ahk_thread.is_alive():
                #self.ahk_thread.kill()
                ctypes.windll.user32.PostThreadMessageW(self.ahk_thread.native_id, win32con.WM_QUIT, 0, 0)
        self.ahk_thread         = _general.KThread(target=self._Thread4ahk)
        if hasattr(self, "lock"):
            if self.lock.locked():
                self.lock.release()
        else:
            self.lock = _general.Lock()
        if hasattr(self, "ahklock"):
            if self.ahklock.locked():
                self.ahklock.release()
        else:
            self.ahklock = _general.Lock()
        if hasattr(self, "ahk_translator"):
            pass
        else:
            self.ahk_translator = _general.ahk()
        if hasattr(self, "error"):
            self.error.clear()
        else:
            self.error = dict()
        if hasattr(self, "install"):
            for i in self.install:
                self.install[i].__del__()
            self.install.clear()
        else:
            self.install = dict()
        if hasattr(self, "menu"):
            self.menu.clear()
        else:
            self.menu = []
        if hasattr(self, "submenus"):
            self.submenus.clear()
        else:
            self.submenus = dict()
        if hasattr(self, "ahk"):
            self.ahk.clear()
        else:
            self.ahk = dict()
        if hasattr(self, "hhk"):
            self.hhk.clear()
        else:
            self.hhk = []
        if hasattr(self, "icos"):
            self.icos.clear()
        else:
            self.icos = []
        if hasattr(self, "main_error"):
            self.main_error.clear()
        else:
            self.main_error = []
        #TODO: clean self.main_sicon in reset
        if hasattr(self, "nb_hotkey"):
            for i in range(self.nb_hotkey):
                ctypes.windll.user32.UnregisterHotKey(None, i)
        self.conf               = os.path.abspath(posixpath.join( self.userdir, self.name+".conf"))
        self.conf_maintheme     = "native"
        self.conf_theme         = "native"
        self.conf_loglevel      = "WARNING"
        self.nb_hotkey          = 0
        self.started            = False
        self.silent             = False
        self.colors             = _icon.colors()
        self.mdark              = ''
        self.mlight             = ''
        self.dark               = ''
        self.light              = ''
        self.mainmenuconf       = _general.mainmenuconf(self.colors, self.images)

    def _Restart(self):
        self._ResetVar()
        #Find and read config file
        config = configparser.ConfigParser(strict=False)
        exist_conf = False
        if os.path.isfile(self.conf) :
            exist_conf = True
        else:
            thispath = os.getcwd()
            for endpath in [[],
                            ["conf"],
                            ["..","conf"],
                            ["..","..","conf"]]:
                path = thispath
                for k in endpath:
                    path = posixpath.join( path, k)
                path = os.path.abspath(posixpath.join( path, self.name+".conf"))
                if os.path.exists(path) and os.path.isfile(path) :
                    self.conf = path
                    exist_conf = True
                    break
        if not exist_conf:
            self.main_error.append("Fail to find configuration")
            self.logger.error("Fail to find configuration")
        else:
            self.logger.info('Configuration found : '+self.conf)
            confs = [self.conf]
            #Find other conf files
            confs += natsort.os_sorted(glob.glob(os.path.join(os.path.dirname(self.conf),'*.conf')))
            if "\\python" in sys.executable:
                confs += natsort.os_sorted(glob.glob(os.path.join(os.path.dirname(self.conf),'*.conf.example')))
            try:
                config.read(confs, encoding="utf8")
            except Exception as e:
                print_error = "Fail to read configuration (" + os.path.dirname(self.conf) + "): " + str(e)
                self.main_error.append(print_error)
                self.logger.error(print_error)
            qss = os.path.abspath(posixpath.join( os.path.dirname(self.conf), self.name+".qss"))
            if os.path.exists(qss) and os.path.isfile(qss):
                f = open(qss,"r")
                lines = '\n'.join(f.readlines())
                f.close()
                self.tray_menu.setStyleSheet(lines);
        #Load GENERAL config to variables
        for section in config.sections():
            if section.title().strip() == self.generalopt.title():
                for k in config[section]:
                    i = k.title()
                    if i == 'MainTheme'.title():
                        self.conf_maintheme = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    elif i == 'Theme'.title():
                        self.conf_theme = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    elif i == 'LogLevel'.title():
                        LevelNamesMapping=logging.getLevelNamesMapping()
                        levelname=_general.GetOpt(str(config[section][k]),_general.type.UPSTRING)
                        if levelname in LevelNamesMapping:
                            self.conf_loglevel = levelname.title()
                            self.logger.setLevel(level=LevelNamesMapping[levelname])
                        else:
                            self.logger.error('LogLevel->'+k+"not supported")
                    elif i == 'Silent'.title():
                        self.silent = _general.GetOpt(str(config[section][k]),_general.type.BOOL)
                    elif i == 'MainDark'.title():
                        self.mdark = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    elif i == 'MainLight'.title():
                        self.mlight = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    elif i == 'Dark'.title():
                        self.dark = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    elif i == 'Light'.title():
                        self.light = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    else :
                        self.logger.error(section+" : "+k+" is not an existing option")
                continue
            if section.title().strip() == self.nativeopt.title():
                for k in config[section]:
                    i = k.title()
                    if i == 'Dark'.title():
                        self.mainmenuconf.dark = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    elif i == 'Light'.title():
                        self.mainmenuconf.light = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    elif i == 'Theme'.title():
                        self.mainmenuconf.theme = _general.GetOpt(str(config[section][k]),_general.type.STRING)
                    elif 'GENERIC_'+i in self.images.getDefault():
                        self.mainmenuconf.icos['GENERIC_'+i] = _general.GetOpt(str(config[section][k]),_general.type.STRING)

        self.colors.copy(self.conf_theme,'custom')
        self.colors.set('custom',self.dark,self.light)
        self.colors.copy('custom','maincustom')
        self.colors.copy(self.conf_maintheme,'maincustom')
        self.colors.set('maincustom',self.mdark,self.mlight)

        self.mainmenuconf.build()

        #Get ico for Tray
        self.iconid = self.images.create(self.name+'-0.svg','','maincustom')
        if not self.images.getPath(self.iconid):
            self.iconid = self.images.create(self.name+'.svg','','maincustom')

        #Set ico to Tray
        self.tray.setIcon(self.images.getIcon(self.iconid))
        self.app.setWindowIcon(self.images.getIcon(self.iconid))

        #Split in general/menu/action
        m_conf=[]
        a_conf=[]
        for section in config.sections():
            if section.title().strip() in [self.generalopt.title(), self.nativeopt.title()]:
                continue      
            for i in config[section]:
                if "\n" in config[section][i]:
                    self.error[section.strip()] = "Indentation issue in '" + section +"'"
                    self.logger.error("Indentation issue in '" + section +"'")
                    continue
            if section in self.error:
                continue
            if "function" in config[section]:
                a_conf.append(section)
                continue
            if "contain" in config[section]:
                m_conf.append(section)
                continue
            section_array = section.casefold().split()
            if self.generalsectionword.casefold() in section_array and len(section_array) == 2:
                section_array.remove(self.generalsectionword.casefold())
                section_found = section_array[0]
                if section_found in self.avail_modules :
                    self.avail_modules[section_found].Parse(config[section])
                    continue
            error = "'"+section+"' is not recognised as action, general configuration or menu"
            self.logger.error(error)
            self.error[section.strip()]=error

        for section in m_conf:
            orig_section=section
            section=section.strip()
            if section in self.error:
                continue
            i=0
            while section in self.install or section in self.submenus:
                i+=1
                section = orig_section+' [Duplicate n°'+str(i)+']'
            new_class = _feature.menu(section,config[orig_section],self)
            if not orig_section.strip()==section:
                new_class.AddError(orig_section+" already set")
            if new_class.IsOK():
                ahk, hhk = new_class.GetHK()
                if len(ahk)>2 and "key" in hhk:
                    if ahk in self.ahk:
                        new_class.AddError("Duplicated ahk " + self.ahk[ahk])
                    else:
                        self.ahk[ahk] = new_class.show
            if not new_class.IsOK():
                self.error[new_class.show] = ""
            self.submenus[new_class.show]=new_class

        for section in a_conf:
            orig_section=section
            section=section.strip()
            if section in self.error:
                continue
            fct = config[section]["function"].casefold()
            if fct.count('.') != 1:
                self.logger.error("'"+fct+"' does not contain exactly 1 '.' in '"+section+"'")
                continue
            module, feat = fct.split(".")
            mod = self.name+'._'+module
            if not mod in sys.modules.keys():
                self.error[section] = "Module '"+module+"' not loaded"
                self.logger.error("Module '"+module+"' not loaded for '"+section+"'")
                continue
            if not fct in self.avail:
                self.error[section] = "'"+feat+"' not defined in module '" +module + "'"
                self.logger.error("'"+feat+"' not defined in module '" +module+"' from '"+section+"')")
                continue
            i=0
            while section in self.install or section in self.submenus:
                i+=1
                section = orig_section+' [Duplicate n°'+str(i)+']'
            new_class = _general.Str2Class(mod,feat)(section,config[orig_section],self)
            if not orig_section.strip()==section:
                new_class.AddError(orig_section+" already set")
            if new_class.IsOK():
                ahk, hhk = new_class.GetHK()
                if len(ahk)>2 and "key" in hhk:
                    if ahk in self.ahk:
                        new_class.AddError("Duplicated ahk " + self.ahk[ahk])
                    else:
                        self.ahk[ahk] = new_class.show
            if not new_class.IsOK():
                self.error[new_class.show] = ""
            self.install[new_class.show]=new_class
            if new_class.IsOK() and new_class.IsInMenu() and not new_class.IsChild() :
                    self.menu.append(new_class.show)

        config.clear()

        # Start ahk_thread and wait for initialisation
        self.ahklock.acquire()
        self.ahk_thread.start()
        if self.ahklock.acquire(timeout=10):
            self.ahklock.release()
            # Finalise menu and associated errors
            for section in self.submenus:
                self.submenus[section].Check()
                if not self.submenus[section].IsOK():
                    self.error[self.submenus[section].show] = ""
                elif self.submenus[section].IsInMenu():
                    self.menu.append(self.submenus[section].show)
            for section in self.install:
                self.install[section].Check()
                if not self.install[section].IsOK():
                    self.error[self.install[section].show] = ""
            # Define menu configured actions
            # loop on modules for main menu and for Not Clickable
            menu_not = PyQt6.QtWidgets.QMenu('Not clickable',self.tray_menu)
            menu_not.setToolTipsVisible(True)
            id = self.images.create('empty','','custom')
            menu_not.setIcon(self.images.getIcon(id))
            for i in self.install:
                if i in self.error:
                    # not filling here since not defined action are in error but not in install
                    continue
                if self.install[i].IsChild():
                    continue
                if i in self.menu:
                    # Main menu
                    act = PyQt6.QtGui.QAction(self.images.getIcon(self.install[i].iconid),i,self.tray_menu)
                    act.triggered.connect(functools.partial(self._ConnectorAction, i))
                    ahk = self.install[i].GetHK()[0]
                    if ahk:
                        act.setToolTip(ahk)
                    if self.install[i].IsService():
                        act.setCheckable(True)
                        if self.install[i].enabled:
                            #act.setChecked(True)
                            act.activate(PyQt6.QtGui.QAction.ActionEvent.Trigger)
                    self.tray_menu.addAction(act)
                    continue
                # Not clickable
                ahk = self.install[i].GetHK()[0]
                if ahk:
                    act = PyQt6.QtGui.QAction(self.images.getIcon(self.install[i].iconid),i,menu_not)
                    act.setToolTip(ahk)
                    act.setDisabled(True)
                    #act.triggered.connect(functools.partial(self._ConnectorNothing, i))
                    menu_not.addAction(act)

            # Sub menus
            self.tray_menu.addSeparator()
            for i in self.submenus:
                if i in self.error:
                    continue
                submenu = PyQt6.QtWidgets.QMenu(i,self.tray_menu)
                submenu.setToolTipsVisible(True)
                submenu.setIcon(self.mainmenuconf.getIcon('Menu'))
                if i in self.menu:
                    # All submenu action
                    act = PyQt6.QtGui.QAction(self.images.getIcon(self.submenus[i].iconid),i,submenu)
                    ahk = self.submenus[i].GetHK()[0]
                    if ahk:
                        act.setToolTip(ahk)
                    act.triggered.connect(functools.partial(self._ConnectorAction, i))
                    submenu.addAction(act)
                    submenu.addSeparator()
                for c in self.submenus[i].GetContain():  
                    act = PyQt6.QtGui.QAction(self.images.getIcon(self.install[c].iconid),c,submenu)
                    ahk = self.install[c].GetHK()[0]
                    if ahk:
                        act.setToolTip(ahk)
                    if c in self.menu:
                        act.triggered.connect(functools.partial(self._ConnectorAction, c))
                    else:
                        act.setDisabled(True)
                    submenu.addAction(act)
                self.tray_menu.addMenu(submenu)

            # loop on modules in error
            menu_err = PyQt6.QtWidgets.QMenu('Errors',self.tray_menu)
            menu_err.setToolTipsVisible(True)
            id = self.images.create('dots','','custom')
            menu_err.setIcon(self.images.getIcon(id))
            id = self.images.create(self.images.getPath(self.iconid),'','custom')
            act=PyQt6.QtGui.QAction(self.images.getIcon(id),self.showname,menu_err)
            info,line = self._buildError(self.showname, "")
            act.setToolTip(info)
            act.triggered.connect(functools.partial(self._ConnectorError, self.showname, info+line))
            if len(self.error) == 0 and len(self.main_error) == 0 :
                act.setDisabled(True)
            menu_err.addAction(act)
            menu_err.addSeparator()
            for i in self.error:
                id = self.images.create('',i[0],'custom')
                act=PyQt6.QtGui.QAction(self.images.getIcon(id),i,menu_err)
                info,line = self._buildError(i, self.error[i])
                act.setToolTip(info)
                act.triggered.connect(functools.partial(self._ConnectorError, i, info+line))
                menu_err.addAction(act)

            self.tray_menu.addSeparator()
            #TODO find not use modules
            #menu_ina = PyQt6.QtWidgets.QMenu('Inactive',self.tray_menu)
            #if not menu_ina.isEmpty():
            #    self.tray_menu.addMenu(menu_ina)
            if not menu_not.isEmpty():
                self.tray_menu.addMenu(menu_not)
            if not menu_err.isEmpty():
                self.tray_menu.addMenu(menu_err)

        self.tray_menu.addSeparator()
        # Define menu default actions
        #ToDo generator Gui
        #ToDo conf Gui
        #ToDo about Gui
        #ToDo update link
        id = self.images.create('pen','','custom')
        act=PyQt6.QtGui.QAction('Generate HotKey',self.tray_menu)
        act.setIcon(self.images.getIcon(id))
        act.setDisabled(True)
        #act.setStatusTip('not developed')
        #act.setShortcut('Ctrl+R')
        self.tray_menu.addAction(act)
        id = self.images.create('conf','','custom')
        act=PyQt6.QtGui.QAction('Show current configuration',self.tray_menu)
        act.setIcon(self.images.getIcon(id))
        act.setDisabled(True)
        self.tray_menu.addAction(act)
        id = self.images.create('query','','custom')
        act=PyQt6.QtGui.QAction('About '+self.showname,self.tray_menu)
        act.setIcon(self.images.getIcon(id))
        act.triggered.connect(self._ConnectorAbout)
        act.setDisabled(True)
        self.tray_menu.addAction(act)
        id = self.images.create('reload','','custom')
        act=PyQt6.QtGui.QAction('Reload '+self.showname,self.tray_menu)
        act.setIcon(self.images.getIcon(id))
        act.triggered.connect(self._Restart)
        self.tray_menu.addAction(act)
        self.tray_menu.addSeparator()
        id = self.images.create('exit','','custom')
        act=PyQt6.QtGui.QAction('Exit '+self.showname,self.tray_menu)
        act.setIcon(self.images.getIcon(id))
        act.triggered.connect(self.__del__)
        self.tray_menu.addAction(act)
        self.tray.setContextMenu(self.tray_menu)

        self.started = True
        # print(self._PrintConf())
        return

    def _PrintConf(self,full=True):
        #TODO: _PrintConf: level for default, all, ?
        config = configparser.ConfigParser()
        config[self.generalopt] = { }
        if self.conf_maintheme or full:
            config[self.generalopt]["MainTheme"]  = self.conf_maintheme 
        if self.conf_theme or full:
            config[self.generalopt]["Theme"]      = self.conf_theme
        if self.conf_loglevel != "WARNING" or full:
            config[self.generalopt]["LogLevel"]   = self.conf_loglevel
        if self.mlight or full:
            config[self.generalopt]["MainLight"]  = self.mlight
        if self.mdark or full:
            config[self.generalopt]["MainDark"]   = self.mdark
        if self.light or full:
            config[self.generalopt]["Light"]      = self.light
        if self.dark or full:
            config[self.generalopt]["Dark"]       = self.dark
        if self.silent or full:
            config[self.generalopt]["Silent"]     = str(self.silent)
        
        config[self.nativeopt] = { }
        for i in self.avail_modules:
            m = self.avail_modules[i].show+' '+self.generalsectionword.title()
            arr = self.avail_modules[i].GetConf(partial=not full)
            if not arr and not full:
                continue
            config[m]={}
            for opt in arr:
                config[m][opt] = arr[opt]
        for i in self.submenus:
            c = ','.join(self.submenus[i].GetContain())
            if not c and not full:
                continue
            config[i]={}
            config[i]["Contains".title()]=','.join(self.submenus[i].GetContain())
            if self.submenus[i].menu or full:
                config[i]["click".title()] = str(self.submenus[i].menu)
            if self.submenus[i].ahk or full:
                config[i]["ahk".title()]=self.submenus[i].ahk
        for i in self.install:
            config[i]={ "function".title() : self.install[i].module+ "." + self.install[i].name}
            #mandatory options
            if self.install[i].menu or full:
                config[i]["click".title()]=str(self.install[i].menu)
            if self.install[i].ahk or full:
                config[i]["ahk".title()]=self.install[i].ahk
            #optional options
            if self.install[i].ico or full:
                config[i]["ico".title()] = self.install[i].ico
            if self.install[i].theme:
                color = self.install[i].theme.split('/')[0]
                if not color == 'custom':
                    if "color" in config[self.install[i].module.upper()]:
                        if color != config[self.install[i].module.upper()]["color"].split('/')[0]:
                            config[i]["color".title()] = color
            if self.install[i].light:
                if "light" in config[self.install[i].module.upper()]:
                    if self.install[i].light != config[self.install[i].module.upper()]["light"]:
                            config[i]["light".title()] = light
            if self.install[i].dark:
                if "dark" in config[self.install[i].module.upper()]:
                    if self.install[i].dark != config[self.install[i].module.upper()]["dark"]:
                            config[i]["dark".title()] = dark
            for opt in self.install[i].GetOpt(sub=not full):
                config[i][opt]=str(getattr(self.install[i], opt))
        f = io.StringIO()
        config.write(f)
        out = f.getvalue()
        f.close()
        return out

    def _Thread4Run(self,args,silent=False):
        if not silent and not self.started:
            silent = True
        if self.silent:
            silent = True
        if args in self.submenus:
            outs=[]
            for a in self.submenus[args].GetContain():
                outs.append(a+": "+self._Thread4Run(a,silent=True))
            _general.PopUp(args, "\n".join(outs))
            return ""
        if not args in self.install:
            return ""
        if self.lock.acquire(timeout=1):   
            action=self.install[args]
            start_time = datetime.datetime.now()
            show = action.show+start_time.strftime(" [%H%M%S]")
            self.logger.debug('Run '+show)
            th = _general.KThread(target=action.Run)
            th.start()
            th.join(10)
            out = th.getout()
            if not silent:
                _general.PopUp(args, out)
            duration = datetime.datetime.now() - start_time
            if th.is_alive():
                self.logger.debug('Kill '+show +' after '+str(duration.seconds)+' sec')
                th.kill()
            else:
                self.logger.debug(show+ ' ran in '+str(duration.seconds)+' sec')
            #few seconds before releasing lock
            #TODO: releasing lock time in configuration
            if not silent:
                time.sleep(3)
            self.logger.debug('Release lock')
            if self.lock.locked(): self.lock.release()
        return out

    def _Thread4ahk(self):
        self.logger.info("Starting ahk thread")
        # Initialisation
        if not self.ahklock.locked():
            self.logger.critical("Fail to get lock to initial ahk thread")
            self.main_error.append("Fail to get lock to initial ahk thread")
        for ahk in self.ahk:
            if self.ahk[ahk] in self.install:
                menu = self.install[self.ahk[ahk]]
            elif self.ahk[ahk] in self.submenus:
                menu = self.submenus[self.ahk[ahk]]
            else:
                self.main_error.append(self.ahk[ahk]+" not found to set "+ahk)
                continue
            if (ctypes.windll.user32.RegisterHotKey(None, self.nb_hotkey+1, menu.hhk["mod"], menu.hhk["key"])):
                self.nb_hotkey += 1
                self.logger.debug("register "+ahk)
            else:
                menu.AddError("Fail to register Hotkey ("+ahk+"): "+ctypes.FormatError(ctypes.GetLastError()))
                self.error[self.ahk[ahk]]=""
        if self.ahklock.locked():
            self.ahklock.release()
        # Waiting
        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                ahk = self.ahk_translator.hhk2ahk({ "mod" : msg.lParam & 0b1111111111111111,
                                     "key" : msg.lParam >> 16})
                if ahk in self.ahk:
                    self._ConnectorAction(self.ahk[ahk])
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        self.logger.info("Ending ahk thread")
        return

    def _Thread4Flush(self):
        logger = logging.getLogger()
        while True:
            logger.handlers[0].flush()
            for i in range(10): time.sleep(1)
        return

    def _ConnectorTray(self,reason):
        if reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            pass
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.Context:
            self.tray_menu.show()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick:
            self._about()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.MiddleClick:
            self.__del__()
        return

    def _ConnectorAction(self,feature):
        if self.lock.locked():
            if feature in self.install:
                self.logger.debug('Lock locked for ' + self.install[feature].show)
            elif feature in self.submenus:
                self.logger.debug('Lock locked for ' + self.submenus[feature].show)
            else:
                self.logger.critical('Lock locked for undefined feature' + feature)
            return
        a=_general.KThread(target=self._Thread4Run,args=[feature])
        a.start()
        return

    def _ConnectorAbout(self):
        return

    def _buildError(self,name,error):
        info = '<ul>\n'
        l=0
        arr=[]
        if error:
            arr=[error]
        elif name == self.showname:
            arr = self.main_error
            for n in self.error:
                if self.error[n]:
                    arr+=[self.error[n]]
                elif n in self.submenus:
                    arr+=self.submenus[n].GetError()
                elif n in self.install:
                    arr+=self.install[n].GetError()
        elif name in self.submenus:
            arr=self.submenus[name].GetError()
        elif name in self.install:
            arr=self.install[name].GetError()
        for e in arr:
            l = max(l,len(e))
            info += '\t<li>' + e + '</li>\n'
        info += '</ul>\n'
        l = 60+min(l,80)
        line = '<p>'
        for i in range(l): line += '&nbsp;'
        line += '</p>'
        return [info, line]

    def _ConnectorError(self,name,info):
        text = '<h3>'+name+' errors</h3>'
        box = PyQt6.QtWidgets.QMessageBox()
        #box.setTextFormat(PyQt6.QtCore.Qt.RichText)
        box.setWindowTitle(self.showname)
        box.setText(text)
        box.setInformativeText(info)
        #box.setStandardButtons(PyQt6.QtWidgets.Ok)
        p = self.images.getIcon(self.iconid).pixmap(20)
        #box.setIconPixmap(p)
        box.setWindowIcon(self.images.getIcon(self.iconid))
        box.exec()
        return
