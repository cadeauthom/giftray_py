import os
import sys
import shutil
import trace, threading
#import win32api         # package pywin32
#import win32con
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

handle_ToolbarWindow32 = []
def _callback_enumChildWindows(handle, arg):
    if win32gui.GetClassName(handle) == arg:
        handle_ToolbarWindow32.append(handle)
    return True

def GetCurrentPath():
    hwnd      = win32gui.GetForegroundWindow()
    classname = win32gui.GetClassName(hwnd)
    #other windows: test if windows name contains a path
    text = win32gui.GetWindowText(hwnd)
    for text in text.split():
        if os.path.isdir(text):
            return text
        if os.path.isfile(text):
            return os.path.dirname(text)
    if (classname == "WorkerW"):
        #Desktop
        return
    if True or (classname == "CabinetWClass") or (classname == "ExploreWClass"):
        #explorer (or other windows ?) if path in ToolbarWindow32
        handle_ToolbarWindow32.clear()
        win32gui.EnumChildWindows(hwnd, _callback_enumChildWindows, "ToolbarWindow32")
        for i in handle_ToolbarWindow32 :
            for text in win32gui.GetWindowText(i).split():
                if os.path.isdir(text):
                    return text
                if os.path.isfile(text):
                    return os.path.dirname(text)    
        return
    return

def RealPath(app):
    if not app:
        return
    return shutil.which(app)

def str_to_class(module,feat):
    return getattr(sys.modules[module], feat)

#no import threading in main with:
Lock = threading.Lock
class KThread(threading.Thread):
    """ CREDIT: https://blog.finxter.com/how-to-kill-a-thread-in-python/
        Method 3
        A subclass of threading.Thread, with a kill()method."""
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False
    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)
    def __run(self):
        """Hacked run function, which installs thetrace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        return None
    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace
    def kill(self):
        self.killed = True
