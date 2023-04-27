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
import PyQt6
import win32api
import ctypes
import math

from . import _feature
from . import _general

# class general(_feature.general):
    # pass

class screen(_feature.main):
    def _Init(self,others,others_general):
    
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        ctypes.windll.user32.SetProcessDPIAware()
        self.allopt += ["split"]
        self.split = ["1x2","1x4"]
        for i in others:
            k = i.casefold()
            if k == "split".casefold():
                self.split = others[i]
                self.setopt.append(k)
            else:
                self.AddError("'"+i+"' not defined")

        monitors = win32api.EnumDisplayMonitors()
        resolutions=dict()
        for idx, m in enumerate(monitors):
            monitor_info = win32api.GetMonitorInfo(m[0])
            #X_sp = monitor_info["Work"][2] - monitor_info["Monitor"][2]
            #Y_sp = monitor_info["Work"][3] - monitor_info["Monitor"][3]
            #X_res = monitor_info["Work"][2] - monitor_info["Work"][0]
            #Y_res = monitor_info["Work"][3] - monitor_info["Work"][1]
            if idx == 0:
                additionnal_X = win32api.GetSystemMetrics(win32con.SM_CXMAXIMIZED) - monitor_info["Work"][2] + monitor_info["Work"][0]
                additionnal_Y = win32api.GetSystemMetrics(win32con.SM_CYMAXIMIZED) - monitor_info["Work"][3] + monitor_info["Work"][1]
            x= monitor_info["Work"][0] - math.ceil(additionnal_X/2)
            y= monitor_info["Work"][1] - math.ceil(additionnal_Y/2)
            width = monitor_info["Work"][2]-monitor_info["Work"][0]+additionnal_X
            height = monitor_info["Work"][3] - monitor_info["Work"][1]+additionnal_Y
            x= monitor_info["Work"][0]
            y= monitor_info["Work"][1]
            width = monitor_info["Work"][2]-monitor_info["Work"][0]
            height = monitor_info["Work"][3] - monitor_info["Work"][1]
            resolutions[int(m[0])]=(x,y,width,height)
        hwnd = win32gui.GetForegroundWindow()
        window = PyQt6.QtGui.QWindow.fromWinId(hwnd)
        size = window.screen().geometry()
        r1=size.getCoords()
        monitor_hwnd = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        print('Resolutions = ',resolutions)
        (X,Y,w,h)=resolutions[int(monitor_hwnd)]
        X_div = 3
        Y_div = 3
        X_border = math.ceil(additionnal_X/(2*X_div))
        Y_border = math.ceil(additionnal_Y/(2*Y_div))
        W_div = w/X_div+4*X_border
        H_div = h/Y_div+4*Y_border
        import time
        for k in range(X_div):
            for l in range(Y_div):
                if k==0:
                    x=X-2*X_border
                    w=W_div
                else:
                    x=X-2*(k+1)*X_border
                    w=W_div
                if l==0:
                    y=Y-2*Y_border
                    h=H_div
                else:
                    y=Y-2*(l+1)*Y_border
                    h=H_div
                # print('Before:' ,win32gui.GetWindowRect(hwnd))
                win32gui.SetWindowPos(hwnd,
                                      0,
                                      int(x + k*W_div),
                                      int(y + l*H_div),
                                      int(w),
                                      int(h),
                                      win32con.SWP_NOZORDER |win32con.SWP_FRAMECHANGED|win32con.SWP_DRAWFRAME)
                print('After :' ,win32gui.GetWindowRect(hwnd))
                # print('Client:' ,win32gui.GetClientRect (hwnd))
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
                # print(hwnd)
                # print(rect)
                # print ('ctypes:' ,(rect.left, rect.top, rect.right, rect.bottom))
                time.sleep(3)
                hwnd = win32gui.GetForegroundWindow()
        # while True:
            # hwnd = win32gui.GetForegroundWindow()
            # print(win32gui.GetWindowRect(hwnd))
            # time.sleep(3)
        return

    def _Run(self):
        print(self.split)

class script(_feature.main):
    def _Init(self,others,others_general):
        self.allopt += ["cmd","args","admin"]
        self.cmd = ""
        self.args = ""
        self.admin = False
        for i in others:
            k = i.casefold()
            if k == "cmd".casefold():
                self.cmd = others[i]
                self.setopt.append(k)
            elif k == "args".casefold():
                self.args = others[i]
                self.setopt.append(k)
            elif k == "admin".casefold():
                self.admin = (others[i].lower().capitalize() == "True")
                self.setopt.append(k)
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
