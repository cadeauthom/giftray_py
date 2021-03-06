import os
import sys
import win32api         # package pywin32
import win32con
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

def ValidateIconPath(path="",color="black",project=""):
    if path:
        path = os.path.abspath(os.path.join(path,color))
        if os.path.isdir(path):
            return path
    path = os.path.abspath(os.path.join( sys.path[0], color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "..\\"+color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "icons\\"+color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "..\\icons\\"+color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "..\\dist\\"+project+"\\icons\\"+color))
    if os.path.isdir(path):
        return path
    path = os.path.abspath(os.path.join( sys.path[0], "..\\build\\"+project+"\\icons\\"+color))
    if os.path.isdir(path):
        return path
    return ""

def GetIcon(path,ico="default_default.ico"):
    last_try=False
    if ico=="default_default.ico":
        last_try=True
    if not ico:
        ico="default_default.ico"
    iconPathName = os.path.abspath(os.path.join( path, ico ))
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    if os.path.isfile(iconPathName):
        try:
            return win32gui.LoadImage(0, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
            pass
    if not last_try:
        return GetIcon(path)
    return win32gui.LoadIcon(0, win32con.IDI_APPLICATION)