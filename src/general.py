import os
import sys
import shutil
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