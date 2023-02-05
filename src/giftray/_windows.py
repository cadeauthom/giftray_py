#import os
#import sys
import subprocess
import win32con
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

from . import _feature
from . import _general

class script(_feature.main):
    def _custom_init(self,others):
        self.cmd = ""
        self.args = ""
        self.admin = False
        for i in others:
            k = i.casefold()
            if k == "cmd".casefold():
                self.cmd = others[i]  
            elif k == "args".casefold():
                self.args = others[i]  
            elif k == "admin".casefold():
                self.admin = (others[i].lower().capitalize() == "True")   
            else:
                self.giftray.logger.error("'"+i+"' not defined in '" +self.show+"'")
                self.error.append("'"+i+"' not defined")
        if not self.cmd:
            self.giftray.logger.error("cmd not set in '" +self.show+"'")
            self.error.append("cmd not set in '" +self.show+"'")
        else:
            cmd = _general.RealPath(self.cmd)
            if not cmd:
                self.giftray.logger.error(cmd + "not found in '" +self.show+"'")
                self.error.append(cmd + "not found in '" +self.show+"'")
            else:
                self.cmd = cmd
        return

    def _custom_get_opt(self):
        return ["cmd","args","admin"]

    def _custom_run(self):
        out = self.cmd
        cmd = '& { Start-Process "'+self.cmd+'"'
        if self.args:
            cmd += ' -ArgumentList "' + self.args+'"'
            out += ' ' + self.args
        if self.admin:
            cmd += ' -Verb RunAs'
            out += ' as admin'
        cmd += '}'
        prog = subprocess.Popen(['Powershell ', '-Command', cmd])
        return out


class alwaysontop(_feature.main):
    def __del__(self):
        self._removeOnTop()

    def _custom_init(self,others):
        self.top_hwnd = None
        self.menu = False
        for i in others:
            k = i.casefold()
            if False:
                pass
            else:
                self.giftray.logger.error("'"+i+"' not defined in '" +self.show+"'")
                self.error.append("'"+i+"' not defined")
        return

    def _custom_get_opt(self):
        return []

    def _custom_run(self):
        _general.GetAllWindowsName()
        hwnd = win32gui.GetForegroundWindow()
        classname = win32gui.GetClassName(hwnd)
        name = "name of the current window"
        self._removeOnTop()
        if not hwnd:
            return "Unable to set windows to top"
        if hwnd == self.top_hwnd:
            return "Unset OnTop to " + name
        if (classname == "WorkerW"):
            if not self.top_hwnd:
                return "Unable to OnTop Desktop"
        print(win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE ))
        win32gui.SetWindowPos(hwnd,
            win32con.HWND_TOPMOST,
            0,0,0,0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        print(win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE ))
        self.top_hwnd = hwnd
        return "Set OnTop to " + name

    def _removeOnTop(self):
        if self.top_hwnd :
            print(win32gui.GetWindowLong(self.top_hwnd, win32con.GWL_STYLE ))
            print('test if win exists')
            print('remove TOPMOST')
            return True
        return False
