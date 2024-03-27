# import os
# import io
# import sys
# import posixpath
import signal
# import inspect
import time
# import datetime
# import glob
# import shutil
#import win32api         # package pywin32
import win32con
# import configparser
import keyboard
# try:
    # import win32gui
# except ImportError:
    # import winxpgui as win32gui
# import win32gui_struct
import ctypes, ctypes.wintypes
import PyQt6.QtWidgets #, PyQt6.QtGui
# import notifypy
# import natsort
# import psutil
import logging

from . import _var
from . import _general
from . import _feature

class giftray():
    def __init__(self):
        def signal_handler(signum, frame):
            self.__del__()
        # Register our signal handler with `SIGINT`(CTRL + C)
        signal.signal(signal.SIGINT, signal_handler)
        # Define app
        self.app = PyQt6.QtWidgets.QApplication([]) # take 50ms
        self.app.setQuitOnLastWindowClosed ( False )
        self.mainWin = PyQt6.QtWidgets.QMainWindow()
        self.statics = _var.statics()

        self.disambiguateTimer = PyQt6.QtCore.QTimer()
        self.disambiguateTimer.setSingleShot(True)
        self.disambiguateTimer.timeout.connect(self._ConnectorAbout)
        # Define tray
        #self.main_ico = _var.main_ico()
        self.tray = PyQt6.QtWidgets.QSystemTrayIcon( # take 30ms
                        self.statics.getIcon())
        self.tray.setToolTip    (self.statics.showname)
        self.tray.setVisible    ( True )
        self.tray.show          ()
        self.tray.activated.connect( self._ConnectorTray )

        self._Restart()
        self.statics.logger.info("Entering wait state")
        self.flush_thread = _general.KThread(target=self._Thread4Flush)
        self.flush_thread.start()
        timer = PyQt6.QtCore.QTimer()
        timer.start(500)  # You may change this if you wish.
        timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

        '''
        c=0
        while True:
            m=int(psutil.Process().memory_info().rss/1024/1024)
            g=m/1024
            if (c%100000 == 0):
                print('(%8u) %8uMb - % 6.2fGb' % (c,m,g))
            c+=1
        '''

        self.app.exec()
        return

    def __del__(self):
        self._Clean()
        if hasattr(self, "flush_thread"):
            _general.threadKiller(self.flush_thread)
        if hasattr(self, "statics"):
            self.statics.logger.info("Exiting application")
            del(self.statics)
        if hasattr(self, "app"):
            self.app.quit()

    def _Clean(self):
        if hasattr(self, "ahk_thread"):
            if self.ahk_thread.is_alive():
                _general.threadKiller(self.ahk_thread)
            if self.ahk_thread.is_alive():
                print('failed to kill ahk_thread')
        if hasattr(self, "dynamics"):
            self.dynamics.locker.acquire(timeout=5)
            self.tray.setContextMenu(None)
            self.tray.setIcon(self.statics.getIcon())
            self.dynamics.__del__()
        if hasattr(self, "dynamics"):
            del(self.dynamics)
        if hasattr(self, "ahklock"):
            if self.ahklock.locked():
                self.ahklock.release()
        else:
            self.ahklock = _general.Lock()

    def _Restart(self):
        self._Clean()
        self.ahk_thread = _general.KThread(target=self._Thread4ahk)
        self.dynamics = _var.dynamics(self.statics,self.tray)

        self.app.setStyle(self.dynamics.getStyle())

        self.tray.setIcon(self.dynamics.getIcon('Tray'))
        self.app.setWindowIcon(self.dynamics.getIcon('Tray'))

        # Start ahk_thread and wait for initialisation
        self.ahklock.acquire()
        self.ahk_thread.start()
        if self.ahklock.acquire(timeout=10):
            self.ahklock.release()
            self.tray.setContextMenu(self.dynamics.buildMenu(self._Restart,self._ConnectorShortCut,self.__del__))

        return

    def _Thread4ahk(self):
        self.statics.logger.info("Starting ahk thread")
        # Initialisation
        if not self.ahklock.locked():
            self.statics.logger.critical("Fail to get lock to initial ahk thread")
            #self.main_error.append("Fail to get lock to initial ahk thread")
        self.dynamics.registerAHK()
        if self.ahklock.locked():
            self.ahklock.release()
        # Waiting
        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                ahk = self.statics.ahk_translator.hhk2ahk(
                                    { "mod" : msg.lParam & 0b1111111111111111,
                                      "key" : msg.lParam >> 16})
                if ahk == self.dynamics.conf["Generals"]['AHK']:
                    self.tray.setIcon(self.statics.icon['Themes'][_var.color.GREEN]['Icon'])
                    for k in self.dynamics.install['Key']:
                        # print(k,' ->',self.statics.ahk_translator.getKey(k))
                        keyboard.on_press_key(k, lambda event: self.dynamics.ConnectorAHK(event.scan_code),suppress=True)
                    time.sleep(2)
                    if self.dynamics.cleanPress():
                        self.tray.setIcon(self.dynamics.getIcon('Tray'))
                    '''
                    arr=[]
                    event = keyboard.read_event(suppress=True)  # Lire un événement clavier sans l'afficher
                    while event.event_type == 'up':
                        arr.append(event.scan_code)
                        print(event.to_json(), keyboard.is_pressed(event.scan_code))
                        event = keyboard.read_event(suppress=True)  # Lire un événement clavier sans l'afficher
                    if event.name in self.dynamics.install['Key']:
                        print(event.name, ' : ', self.dynamics.install['Key'][event.name])
                    else:
                        print('nope; ', event.to_json())
                    for i in arr:
                        print(keyboard.is_pressed(event.scan_code))
                        keyboard.release(i)
                        print(keyboard.is_pressed(event.scan_code))
                    '''
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        self.statics.logger.info("Ending ahk thread")
        return

    def _Thread4Flush(self):
        logger = logging.getLogger()
        while True:
            self.statics.writeLockFile()
            logger.handlers[0].flush()
            for i in range(10): time.sleep(1)
        return

    def _ConnectorTray(self,reason):
        if reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            self.disambiguateTimer.start(self.app.doubleClickInterval())
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.Context:
            if hasattr(self, "dynamics"):
                self.dynamics.show()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick:
            self.disambiguateTimer.stop()
            self.mainWin.hide()
            self.__del__()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.MiddleClick:
            #seems not detected as midlle but as trigger
            pass
        return

    def _ConnectorAbout(self):
        if not self.mainWin.centralWidget():
            self.mainWin.setFixedHeight(int(100*2.5))
            self.mainWin.setFixedWidth(400)
            # self.mainWin.resize(500, 500)
            if hasattr(self, "statics"):
                #PyQt6.QtWidgets.QWidget(
                self.mainWin.setWindowTitle('About ' + self.statics.showname)
                if hasattr(self, "dynamics"):
                    self.mainWin.setWindowIcon(self.dynamics.getIcon('Tray'))
                else:
                    self.mainWin.setWindowIcon(self.statics.getIcon())
                self.mainWin.setCentralWidget(self.statics.getAbout())
        if self.mainWin.isVisible():
            self.mainWin.hide()
        else:
            self.mainWin.show()
        return

    def _ConnectorShortCut(self):
        sc = PyQt6.QtWidgets.QMainWindow()
        sc.setCentralWidget(self.dynamics.getShortCut())
        sc.show()