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
import time

from . import _feature
from . import _general

# class general(_feature.general):
    # pass

class script(_feature.action):
    def _Init(self,others,others_general):
        self.allopt += ["cmd","args","admin"]
        self.cmd = ""
        self.args = ""
        self.admin = False
        for i in others:
            k = i.casefold()
            if k == "cmd".casefold():
                self.cmd = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
            elif k == "args".casefold():
                self.args = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
            elif k == "admin".casefold():
                self.admin = _general.GetOpt(others[i],_general.type.BOOL)
                self.setopt.append(k)
            else:
                self.AddError("'"+i+"' not defined")
        if not self.cmd:
            self.AddError("cmd not set in '" +self.show+"'")
        else:
            cmd = _general.WindowsHandler().GetRealPath(self.cmd)
            if not cmd:
                self.AddError(self.cmd + " not found in '" +self.show+"'")
            else:
                self.cmd = cmd
        return

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

class stayactive(_feature.service):
    def _Init(self,others,others_general):
        self.allopt += ["frequency"]
        self.frequency = 60
        for i in others:
            k = i.casefold()
            if k == "frequency".casefold():
                a = _general.GetOpt(others[k],_general.type.UINT)
                if a:
                    self.frequency = a
            else:
                self.AddError("'"+i+"' not defined")

    def _Run(self):
        import clicknium
        a,b = clicknium.mouse.position()
        while True:
            for i in range(self.frequency): time.sleep(1)
            x,y = clicknium.mouse.position()
            if x==a and y==b:
              clicknium.mouse.move(a,b)
            a,b = clicknium.mouse.position()
        return

class alwaysontop(_feature.action):
    def __del__(self):
        currentOnTop = _general.WindowsHandler().GetAllOnTopWindowsName()
        for hwnd in self.top_hwnd:
            if hwnd in currentOnTop:
                win32gui.SetWindowPos(hwnd,
                    win32con.HWND_NOTOPMOST,
                    0,0,0,0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        _feature.action.__del__(self)

    def _Init(self,others,others_general):
        self.allopt += []
        self.top_hwnd = set()
        self.menu = False
        for i in others:
            k = i.casefold()
            if False:
                pass
            else:
                self.AddError("'"+i+"' not defined")
        return

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
