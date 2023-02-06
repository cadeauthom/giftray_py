#import os
#import sys
import subprocess
import win32con
import win32process
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui
import psutil

from . import _feature
from . import _general

class script(_feature.main):
    def _Init(self,others):
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
                self.AddError("'"+i+"' not defined")
        if not self.cmd:
            self.AddError("cmd not set in '" +self.show+"'")
        else:
            cmd = _general.WindowsHandler().GetRealPath(self.cmd)
            if not cmd:
                self.AddError(cmd + "not found in '" +self.show+"'")
            else:
                self.cmd = cmd
        return

    def _GetOpt(self):
        return ["cmd","args","admin"]

    def _Run(self):
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
        currentOnTop = _general.WindowsHandler().GetAllOnTopWindowsName()
        for hwnd in self.top_hwnd:
            if hwnd in currentOnTop:
                win32gui.SetWindowPos(hwnd,
                    win32con.HWND_NOTOPMOST,
                    0,0,0,0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def _Init(self,others):
        self.top_hwnd = set()
        self.menu = False
        for i in others:
            k = i.casefold()
            if False:
                pass
            else:
                self.AddError("'"+i+"' not defined")
        return

    def _GetOpt(self):
        return []

    def _Run(self):
        hwnd = win32gui.GetForegroundWindow()
        classname = win32gui.GetClassName(hwnd)
        if (classname == "WorkerW"):
            return "Unable to OnTop Windows Desktop"
        if (classname == "Shell_TrayWnd"):
            return "Unable to OnTop Windows Tray"
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        name = psutil.Process(pid).name()
        currentOnTop = _general.WindowsHandler().GetAllOnTopWindowsName()
        if not hwnd:
            return "Unable to set windows to top"
        if hwnd in self.top_hwnd:
            # we set it TopMost
            self.top_hwnd.remove(hwnd)
            if hwnd in currentOnTop:
                # it is TopMost
                # NoTopMost the window
                win32gui.SetWindowPos(hwnd,
                    win32con.HWND_NOTOPMOST,
                    0,0,0,0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                return('UnTop '+name)
            else:
                return('(Already) UnTop '+name)
        if hwnd in currentOnTop:
            # already TopMost (don't touch)
            return('OnTop of '+name+'managed outside of '+self.show)
        # NoTopMost the window
        win32gui.SetWindowPos(hwnd,
            win32con.HWND_TOPMOST,
            0,0,0,0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        self.top_hwnd.add(hwnd)
        return "Set OnTop to " + name
