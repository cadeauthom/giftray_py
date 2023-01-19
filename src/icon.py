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


def ValidateIconPath(path="",color="black",project=""):
    #return _ValidateIconPath_sub(path,color,project).replace('\\','/')
    #a=_ValidateIconPath_sub(path,color,project).replace('/','\\')
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
    standardIcon = giftray.win_main.style().standardIcon(
                        PyQt6.QtWidgets.QStyle.StandardPixmap.SP_TitleBarContextHelpButton)
    return standardIcon, hicon, ""
    
# def GetIcon(path,ico="default_default.ico"):
    # if not ico:
        # ico="default_default.ico"
    # icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    # last_try=False
    # if ico=="default_default.ico":
        # last_try=True
    # iconPathName = os.path.abspath(posixpath.join( path, ico )).replace('\\','/')
    # if os.path.isfile(iconPathName):
        # try:
            # hicon = win32gui.LoadImage(0, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
            # return hicon, iconPathName
        # except:
            # pass
    # if not last_try:
        # return GetIcon(path)
    # hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    # return hicon, ""