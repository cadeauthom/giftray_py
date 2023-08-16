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
        self.tray = PyQt6.QtWidgets.QSystemTrayIcon( # take 30ms
                        PyQt6.QtWidgets.QWidget().style().standardIcon( #or self.win_handler
                            PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion))
        self.tray.setToolTip    (self.mainvar.showname)
        self.tray.setVisible    ( True )
        self.tray.show          ()
        self.tray.activated.connect( self._ConnectorTray )

        self._Restart()
        self.mainvar.logger.info("Entering wait state")
        self.th = _general.KThread(target=self._Thread4Flush)
        self.th.start()
        timer = PyQt6.QtCore.QTimer()
        timer.start(500)  # You may change this if you wish.
        timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
        self.app.exec()
        return

    def __del__(self):
        import threading
        if hasattr(self, "ahk_thread"):
            if self.ahk_thread.is_alive():
                #self.ahk_thread.kill()
                ctypes.windll.user32.PostThreadMessageW(self.ahk_thread.native_id, win32con.WM_QUIT, 0, 0)
        if hasattr(self, "app"):
            self.app.quit()
        if hasattr(self, "mainvar"):
            self.mainvar.removeLockFile()
            self.mainvar.logger.info("Exiting application")
        if hasattr(self, "trayconf"):
            self.trayconf.__del__()
        if self.th.is_alive():
            self.mainvar.logger.info('Kill flusher')
            #self.th.kill()
            ctypes.windll.user32.PostThreadMessageW(self.ahk_thread.native_id, win32con.WM_QUIT, 0, 0)
        for thread in threading.enumerate():
            print(thread.name)

    def _Restart(self):
        if hasattr(self, "ahk_thread"):
            if self.ahk_thread.is_alive():
                #self.ahk_thread.kill()
                ctypes.windll.user32.PostThreadMessageW(self.ahk_thread.native_id, win32con.WM_QUIT, 0, 0)
        if hasattr(self, "ahklock"):
            if self.ahklock.locked():
                self.ahklock.release()
        else:
            self.ahklock = _general.Lock()
        self.ahk_thread = _general.KThread(target=self._Thread4ahk)
        self.trayconf = _var.trayconf(self.mainvar)
        self.mainvar.setTray(self.trayconf)
        self.trayconf.load()
        # self.trayconf.print()
        self.app.setStyle(self.trayconf.getStyle())

        self.tray.setIcon(self.trayconf.getIcon('Tray'))
        self.app.setWindowIcon(self.trayconf.getIcon('Tray'))

        # Start ahk_thread and wait for initialisation
        self.ahklock.acquire()
        self.ahk_thread.start()
        if self.ahklock.acquire(timeout=10):
            self.ahklock.release()
            self.tray.setContextMenu(self.trayconf.buildMenu(self._Restart,self.__del__))

        return

    def _Thread4ahk(self):
        self.mainvar.logger.info("Starting ahk thread")
        # Initialisation
        if not self.ahklock.locked():
            self.mainvar.logger.critical("Fail to get lock to initial ahk thread")
            #self.main_error.append("Fail to get lock to initial ahk thread")
        self.trayconf.registerAHK()
        if self.ahklock.locked():
            self.ahklock.release()
        # Waiting
        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                ahk = self.mainvar.ahk_translator.hhk2ahk(
                                    { "mod" : msg.lParam & 0b1111111111111111,
                                      "key" : msg.lParam >> 16})
                if ahk in self.trayconf.install['AHK']:
                    self.trayconf.ConnectorAHK(ahk)
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
            self.trayconf.show()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick:
            self.__del__()
        elif reason == PyQt6.QtWidgets.QSystemTrayIcon.ActivationReason.MiddleClick:
            #seems not detected as midlle but as trigger
            pass
        return

    def _ConnectorAbout(self):
        return

