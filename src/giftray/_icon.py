import os
import posixpath
import sys
#import win32api         # package pywin32
import win32con
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui
import PyQt6.QtWidgets, PyQt6.QtGui, PyQt6.QtSvg
import logging
#https://www.svgrepo.com/collection/variety-duotone-line-icons/

def _GetTrayIcon(rec):
    try:
        return win32gui.CreateIconFromResource(rec, True)
    except:
        return
    
def GetTrayIcon(color="black",project=""):
    try:
        p = os.getcwd()
        for k in ["build","exe"]:
            p = posixpath.join(p, k)
        p = os.path.abspath(posixpath.join( p, project+".exe"))
        if not os.path.isfile(p):
            p=sys.executable
        # hlib = win32api.LoadLibrary(p)
        # icon_names = win32api.EnumResourceNames(hlib, win32con.RT_ICON)
        # for icon_name in icon_names:
            # rec = win32api.LoadResource(hlib, win32con.RT_ICON, icon_name)
            # pmap = QtGui.QPixmap()
            # pmap.loadFromData(rec)
            # icon = PyQt6.QtGui.QIcon(pmap)
            # hicon = _GetTrayIcon(rec)
            # if hicon:
                # return hicon
        # print(p)
        # icons = win32gui.ExtractIconEx(p, 0,10)
        # print(icons)
        # info = win32gui.GetIconInfo(icons[0][0])
        # print(dir(PyQt6.QtGui.QPixmap))
        # pixmap = PyQt6.QtGui.QPixmap.fromWinHBITMAP(info[4])
        # print(pixmap)
        # info[3].close()
        # print(info[3])
        # info[4].close()
        # print(info[4])
        # icon=PyQt6.QtGui.QIcon(pixmap)
        # print(icon)
        # return icon
    except:
        pass
    # too dark
    #return PyQt6.QtWidgets.QWidget().style().standardIcon(PyQt6.QtWidgets.QStyle.StandardPixmap.SP_DialogHelpButton)
    return PyQt6.QtWidgets.QWidget().style().standardIcon( PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion)

def ValidateIconPath(path="",color="black",project=""):
    return _ValidateIconPath_sub(path,color,project).replace('\\','/')

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
    arrpath = []
    if not "\\python" in sys.executable:
        arrpath.append(os.path.dirname(sys.executable))
    arrpath.append(os.getcwd())
    for thispath in arrpath:
        for endpath in [["icons"],["..","icons"],["build","icons"],["build","exe","icons"],["..","build","icons"]]:
            path = thispath
            for k in endpath:
                path = posixpath.join( path, k)
            path = os.path.abspath(posixpath.join( path, color))
            if _Test_Path(path):
                return path
    return ""

def GetIcon(path,giftray,ico="default_default.ico"):
    # picon="svg/android_connect.svg"
    # with open(picon, 'r') as file:
        # img_str = file.read()
    # img_str=img_str.replace("000000","32CD32")
    # img_str=img_str.replace("DDDDDD","FDC75B")
    # svg_renderer = PyQt6.QtSvg.QSvgRenderer(PyQt6.QtCore.QByteArray(img_str.encode()))
    # image = PyQt6.QtGui.QImage(64,64, PyQt6.QtGui.QImage.Format.Format_ARGB32)
    # svg_renderer.render(PyQt6.QtGui.QPainter(image))
    # pixmap = PyQt6.QtGui.QPixmap.fromImage(image)
    # icon = PyQt6.QtGui.QIcon(pixmap)
    # return icon, picon
    if not ico:
        ico="default_default.ico"
    last_try=False
    if ico=="default_default.ico":
        last_try=True
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    if ':' in ico:
        iconPathName = os.path.abspath(ico).replace('\\','/')
    else:
        iconPathName = os.path.abspath(posixpath.join( path, ico )).replace('\\','/')
    if os.path.isfile(iconPathName):
        try:
            standardIcon = PyQt6.QtGui.QIcon(iconPathName)
            #hicon = win32gui.LoadImage(0, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
            if standardIcon.availableSizes() != []:
                return standardIcon, iconPathName
        except:
            pass
    if not last_try:
        return GetIcon(path,giftray)
    #hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    standardIcon = PyQt6.QtWidgets.QWidget().style().standardIcon(
                        #PyQt6.QtWidgets.QStyle.StandardPixmap.SP_TitleBarContextHelpButton) #too dark
                        PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion) #too dark
    return standardIcon, ""
