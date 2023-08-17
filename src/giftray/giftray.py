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
import ctypes, ctypes.wintypes
import PyQt6.QtWidgets, PyQt6.QtGui
import notifypy
import functools
import natsort
import psutil
import logging

from . import _var
from . import _general
from . import _feature

class giftray(object):
    def __init__(self):
        def signal_handler(signum, frame):
            self.__del__()
        # Register our signal handler with `SIGINT`(CTRL + C)
        signal.signal(signal.SIGINT, signal_handler)
        self.mainvar = _var.mainvar()
        # Define app
        self.app = PyQt6.QtWidgets.QApplication([]) # take 50ms
        self.app.setQuitOnLastWindowClosed ( False )
        # Define tray
        self.main_ico = _var.main_ico()
        self.tray = PyQt6.QtWidgets.QSystemTrayIcon( # take 30ms
                        self.main_ico.get())
        self.tray.setToolTip    (self.mainvar.showname)
        self.tray.setVisible    ( True )
        self.tray.show          ()
        self.tray.activated.connect( self._ConnectorTray )

        self._Restart()
        self.mainvar.logger.info("Entering wait state")

        th = _general.KThread(target=self._Thread4Flush)
        th.start()
        timer = PyQt6.QtCore.QTimer()
        timer.start(500)  # You may change this if you wish.
        timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
        self.app.exec()
        if th.is_alive():
            self.mainvar.logger.debug('Kill flusher')
            th.kill()
        return

    def __del__(self):
        if hasattr(self, "app"):
            self.app.quit()
        if hasattr(self, "mainvar"):
            self.mainvar.removeLockFile()
            self.mainvar.logger.info("Exiting")

    def _Restart(self):
        if hasattr(self, "trayconf"):
            self.tray.setContextMenu(None)
            self.tray.setIcon(self.main_ico.get())
            del(self.trayconf)
        self.trayconf = _var.trayconf(self.mainvar)
        self.mainvar.setTray(self.trayconf)
        self.trayconf.load()
        # self.trayconf.print()
        self.app.setStyle(self.trayconf.getStyle())

        self.tray.setIcon(self.trayconf.getIcon('GENERIC_Tray'))
        self.app.setWindowIcon(self.trayconf.getIcon('GENERIC_Tray'))

        '''
        if hasattr(self, "ahk_thread"):
            if self.ahk_thread.is_alive():
                #self.ahk_thread.kill()
                ctypes.windll.user32.PostThreadMessageW(self.ahk_thread.native_id, win32con.WM_QUIT, 0, 0)
        self.ahk_thread         = _general.KThread(target=self._Thread4ahk)

        if hasattr(self, "nb_hotkey"):
            for i in range(self.nb_hotkey):
                ctypes.windll.user32.UnregisterHotKey(None, i)
        self.nb_hotkey=0

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
        '''
        '''
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
            menu_not.setIcon(self.mainmenuconf.getIcon('No-Click'))
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
                #submenu.setIcon(self.mainmenuconf.getIcon('Menu'))
                submenu.setIcon(self.images.getIcon(self.submenus[i].iconid))
                if i in self.menu:
                    # All submenu action
                    #act = PyQt6.QtGui.QAction(self.images.getIcon(self.submenus[i].iconid),i,submenu)
                    act = PyQt6.QtGui.QAction(self.mainmenuconf.getIcon('Menu'),i,submenu)
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
            if len(self.error) == 0:
                act=PyQt6.QtGui.QAction(self.mainmenuconf.getIcon('Errors'),'Errors',self.tray_menu)
            else:
                menu_err = PyQt6.QtWidgets.QMenu('Errors',self.tray_menu)
                menu_err.setToolTipsVisible(True)
                menu_err.setIcon(self.mainmenuconf.getIcon('Errors'))
                act=PyQt6.QtGui.QAction(self.mainmenuconf.getIcon('Errors'),self.showname,menu_err)
            info,line = self._buildError(self.showname, "")
            act.setToolTip(info)
            act.triggered.connect(functools.partial(self._ConnectorError, self.showname, info+line))
            if len(self.error) == 0 and len(self.main_error) == 0 :
                act.setDisabled(True)
            if len(self.error) == 0:
                pass
            else:
                menu_err.addAction(act)
                menu_err.addSeparator()
                for i in self.error:
                    id = self.images.create('',i[0],'other')
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
            if len(self.error) == 0:
                self.tray_menu.addAction(act)
            elif not menu_err.isEmpty():
                self.tray_menu.addMenu(menu_err)

        self.tray_menu.addSeparator()
        menu_help = PyQt6.QtWidgets.QMenu('Help',self.tray_menu)
        menu_help.setToolTipsVisible(True)
        menu_help.setIcon(self.mainmenuconf.getIcon('Help'))

        # Define menu default actions
        #ToDo generator Gui
        #ToDo conf Gui
        #ToDo about Gui
        #ToDo update link
        # act=PyQt6.QtGui.QAction('Generate HotKey',self.tray_menu)
        # act.setIcon(self.mainmenuconf.getIcon('Generator'))
        # act.setDisabled(True)
        # #act.setStatusTip('not developed')
        # self.tray_menu.addAction(act)
        # act=PyQt6.QtGui.QAction('Show current configuration',self.tray_menu)
        # act.setIcon(self.mainmenuconf.getIcon('Configuration'))
        # act.setDisabled(True)
        # self.tray_menu.addAction(act)
        # act=PyQt6.QtGui.QAction('About '+self.showname,self.tray_menu)
        # act.setIcon(self.mainmenuconf.getIcon('About'))
        # act.triggered.connect(self._ConnectorAbout)
        # act.setDisabled(True)
        # self.tray_menu.addAction(act)
        act=PyQt6.QtGui.QAction('Reload configuration',menu_help)
        act.setIcon(self.mainmenuconf.getIcon('Reload'))
        act.triggered.connect(self._Restart)
        menu_help.addAction(act)
        self.tray_menu.addMenu(menu_help)

        act=PyQt6.QtGui.QAction('Exit '+self.showname,self.tray_menu)
        act.setIcon(self.mainmenuconf.getIcon('Exit'))
        act.triggered.connect(self.__del__)
        self.tray_menu.addAction(act)
        self.tray.setContextMenu(self.tray_menu)

        self.started = True
        '''
        self.tray.setContextMenu(self.trayconf.buildMenu(self._Restart,self.__del__))
        return

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
            self.mainvar.logger.debug('Run '+show)
            th = _general.KThread(target=action.Run)
            th.start()
            th.join(10)
            out = th.getout()
            if not silent:
                _general.PopUp(args, out)
            duration = datetime.datetime.now() - start_time
            if th.is_alive():
                self.mainvar.logger.debug('Kill '+show +' after '+str(duration.seconds)+' sec')
                th.kill()
            else:
                self.mainvar.logger.debug(show+ ' ran in '+str(duration.seconds)+' sec')
            #few seconds before releasing lock
            #TODO: releasing lock time in configuration
            if not silent:
                time.sleep(3)
            self.mainvar.logger.debug('Release lock')
            if self.lock.locked(): self.lock.release()
        return out

    def _Thread4ahk(self):
        self.mainvar.logger.info("Starting ahk thread")
        # Initialisation
        if not self.ahklock.locked():
            self.mainvar.logger.critical("Fail to get lock to initial ahk thread")
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
                self.mainvar.logger.debug("register "+ahk)
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
        self.mainvar.logger.info("Ending ahk thread")
        return

    def _Thread4Flush(self):
        logger = logging.getLogger()
        while True:
            self.mainvar.writeLockFile()
            logger.handlers[0].flush()
            for i in range(10): time.sleep(1)
        return

    def _ConnectorTray(self,reason):
        if reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            self._ConnectorAbout()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.Context:
            if hasattr(self, "trayconf"):
                self.trayconf.show()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick:
            self.__del__()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.MiddleClick:
            #seems not detected as midlle but as trigger
            pass
        return

    def _ConnectorAction(self,feature):
        if self.lock.locked():
            if feature in self.install:
                self.mainvar.logger.debug('Lock locked for ' + self.install[feature].show)
            elif feature in self.submenus:
                self.mainvar.logger.debug('Lock locked for ' + self.submenus[feature].show)
            else:
                self.mainvar.logger.critical('Lock locked for undefined feature' + feature)
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
        #p = self.mainmenuconf.getIcon('Main').pixmap(20)
        #box.setIconPixmap(p)
        box.setWindowIcon(self.mainmenuconf.getIcon('Tray'))
        box.exec()
        return
