import os
import posixpath
import sys
import win32api         # package pywin32
import win32con
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui
import PyQt6.QtWidgets, PyQt6.QtGui

def _GetTrayIcon(rec):
    try:
        return win32gui.CreateIconFromResource(rec, True)
    except:
        return
    
def GetTrayIcon(color="black",project=""):
    try:
        p=os.getcwd()+"/build/"+project+"/"+project+".exe"
        if not os.path.isfile(p):
            p=sys.executable
        hlib = win32api.LoadLibrary(p)
        icon_names = win32api.EnumResourceNames(hlib, win32con.RT_ICON)
        for icon_name in icon_names:
            rec = win32api.LoadResource(hlib, win32con.RT_ICON, icon_name)
            hicon = _GetTrayIcon(rec)
            if hicon:
                return hicon
    except:
        pass
    return PyQt6.QtWidgets.QWidget().style().standardIcon(PyQt6.QtWidgets.QStyle.StandardPixmap.SP_DialogHelpButton)

def ValidateIconPath(path="",color="black",project=""):
    return _ValidateIconPath_sub(path,color,project).replace('/','\\')

def _Test_Path(path):
    if not os.path.isdir(path):
        return False
    if not(any(File.endswith(".ico") for File in os.listdir(path))):
        return False
    return True

def _ValidateIconPath_sub(path="",color="black",project=""):
    input_path = path
    if path:
        path = os.path.abspath(posixpath.join(path,color))
        if _Test_Path(path):
            return path
    if not color:
        return _ValidateIconPath_sub(path=input_path,color="blue",project=project)
    path = os.path.abspath(posixpath.join( sys.path[0], color))
    if _Test_Path(path):
        return path
    path = os.path.abspath(posixpath.join( sys.path[0], "..",color))
    if _Test_Path(path):
        return path
    path = os.path.abspath(posixpath.join( sys.path[0], "icons", color))
    if _Test_Path(path):
        return path
    path = os.path.abspath(posixpath.join( sys.path[0], "..", "icons", color))
    if _Test_Path(path):
        return path
    path = os.path.abspath(posixpath.join( sys.path[0], "..", "dist", project, "icons", color))
    if _Test_Path(path):
        return path
    path = os.path.abspath(posixpath.join( sys.path[0], "..", "build", project, "icons", color))
    if _Test_Path(path):
        return path
    return ""

def GetIcon(path,giftray,ico="default_default.ico"):
    if not ico:
        ico="default_default.ico"
    last_try=False
    if ico=="default_default.ico":
        last_try=True
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    iconPathName = os.path.abspath(posixpath.join( path, ico )).replace('\\','/')
    if os.path.isfile(iconPathName):
        try:
            standardIcon = PyQt6.QtGui.QIcon(iconPathName)
            hicon = win32gui.LoadImage(0, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
            if standardIcon.availableSizes() != []:
                return standardIcon, hicon, iconPathName
        except:
            pass
    if not last_try:
        return GetIcon(path,giftray)
    hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    standardIcon = PyQt6.QtWidgets.QWidget().style().standardIcon(
                        PyQt6.QtWidgets.QStyle.StandardPixmap.SP_TitleBarContextHelpButton)
    return standardIcon, hicon, ""
