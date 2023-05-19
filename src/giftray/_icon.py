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


class colors:
    class darklight:
        def __init__(self,dark,light):
            self.dark  = '000000'
            self.light = 'AAAAAA'
            self.update(dark,light)
        def update(self,dark,light):
            if len(dark)==6:
                self.dark  = dark
            if len(light)==6:
                self.light = light
    def __init__(self):
        self.colors = {}
        self.set('default','2ca9bc','000000')
        self.set('black','','')
        self.set('white','FFFFFF','')
        self.set('blue' ,'1185E1','4DCFE1')
        self.set('green','32CD32','7CFC00')
        self.set('red'  ,'ED664C','FDC75B')
    def copy(self,copy,new):
        if copy in self.colors:
            self.set(new,self.colors[copy].dark,self.colors[copy].light)
        else:
            self.set(new,'','')
    def set(self,color,dark,light):
        if len(color)>1:
            if color in self.colors:
                self.colors[color].update(dark,light)
            else:
                self.colors[color] = self.darklight(dark,light)
    def get(self,color):
        if color in self.colors:
            return self.colors[color]
        else:
            return self.colors["default"]
    # def list(self):
        # for color in self.colors:
            # self.show(color)
    # def show(self,color):
            # print(color,self.colors[color].dark,self.colors[color].light)

# def _GetTrayIcon(rec):
    # try:
        # return win32gui.CreateIconFromResource(rec, True)
    # except:
        # return
    
# def GetTrayIcon(color="black",project=""):
    # try:
        # p = os.getcwd()
        # for k in ["build","exe"]:
            # p = posixpath.join(p, k)
        # p = os.path.abspath(posixpath.join( p, project+".exe"))
        # if not os.path.isfile(p):
            # p=sys.executable
        # # hlib = win32api.LoadLibrary(p)
        # # icon_names = win32api.EnumResourceNames(hlib, win32con.RT_ICON)
        # # for icon_name in icon_names:
            # # rec = win32api.LoadResource(hlib, win32con.RT_ICON, icon_name)
            # # pmap = QtGui.QPixmap()
            # # pmap.loadFromData(rec)
            # # icon = PyQt6.QtGui.QIcon(pmap)
            # # hicon = _GetTrayIcon(rec)
            # # if hicon:
                # # return hicon
        # # print(p)
        # # icons = win32gui.ExtractIconEx(p, 0,10)
        # # print(icons)
        # # info = win32gui.GetIconInfo(icons[0][0])
        # # print(dir(PyQt6.QtGui.QPixmap))
        # # pixmap = PyQt6.QtGui.QPixmap.fromWinHBITMAP(info[4])
        # # print(pixmap)
        # # info[3].close()
        # # print(info[3])
        # # info[4].close()
        # # print(info[4])
        # # icon=PyQt6.QtGui.QIcon(pixmap)
        # # print(icon)
        # # return icon
    # except:
        # pass
    # # too dark
    # #return PyQt6.QtWidgets.QWidget().style().standardIcon(PyQt6.QtWidgets.QStyle.StandardPixmap.SP_DialogHelpButton)
    # return PyQt6.QtWidgets.QWidget().style().standardIcon( PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion)

# def ValidateIconPath(path="",color="black",project=""):
    # return _ValidateIconPath_sub(path,color,project).replace('\\','/')

# def _Test_Path(path):
    # if not os.path.isdir(path):
        # return False
    # if not(any(File.endswith(".ico") for File in os.listdir(path))):
        # return False
    # return True

# def _ValidateIconPath_sub(path="",color="black",project=""):
    # input_path = path
    # if path:
        # path = os.path.abspath(posixpath.join(path,color))
        # if _Test_Path(path):
            # return path
    # if not color:
        # return _ValidateIconPath_sub(path=input_path,color="blue",project=project)
    # arrpath = []
    # if not "\\python" in sys.executable:
        # arrpath.append(os.path.dirname(sys.executable))
    # arrpath.append(os.getcwd())
    # for thispath in arrpath:
        # for endpath in [["icons"],["..","icons"],["build","icons"],["build","exe","icons"],["..","build","icons"]]:
            # path = thispath
            # for k in endpath:
                # path = posixpath.join( path, k)
            # path = os.path.abspath(posixpath.join( path, color))
            # if _Test_Path(path):
                # return path
    # return ""

class svgIcons:
    class singleIcon:
        def _GetSVG(self,svg,letter,conf):
            psvgs=[]
            if svg:
                psvg = os.path.abspath(svg)
                if os.path.exists(psvg) and psvg.endswith('.svg'):
                    return(psvg)
                if not svg.endswith('.svg'):
                    psvgs.append(svg+'.svg')
                else:
                    psvgs.append(svg)
            if letter and len(letter)==1 and letter in 'abcdefghijklmnopqrstuvwxyz1234567890':
                psvgs.append('letters/'+letter.casefold()+'.svg')
            else:
                psvgs.append('letters/number-circle-fill.svg')
            arrpath = []
            if not '\\python' in sys.executable:
                arrpath.append(os.path.dirname(sys.executable))
            arrpath.append(os.path.dirname(conf))
            arrpath.append(os.getcwd())
            for psvg in psvgs:
                for thispath in arrpath:
                    for endpath in [['svg'],['..','svg'],['build','svg'],['build','exe','svg'],['..','build','svg']]:
                        path = thispath
                        for k in endpath:
                            path = posixpath.join(path,k)
                        path = os.path.abspath(posixpath.join( path, psvg))
                        if os.path.exists(path):
                            return(path)
            return("")
        def __init__(self,giftray, svg, letter, color):
            self.colors = giftray.colors
            self.color = color
            self.psvg = self._GetSVG(svg,letter,giftray.conf)
            if not self.psvg:
                self.id = "SP_MessageBoxQuestion"
            else:
                c = giftray.colors.get(color)
                self.id=self.psvg+'/'+c.dark+'/'+c.light
        def Build(self):
            if not self.psvg or self.id == 'SP_MessageBoxQuestion':
                self.id   = 'SP_MessageBoxQuestion'
                self.psvg = ''
                self.icon = PyQt6.QtWidgets.QWidget().style().standardIcon(
                                #PyQt6.QtWidgets.QStyle.StandardPixmap.SP_TitleBarContextHelpButton) #too dark
                                PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion) #too dark
                return
            try:
                with open(self.psvg, 'r') as file:
                    img_str = file.read()
                c = self.colors.get(self.color)
                default = self.colors.get('default')
                if c.dark != default.dark:
                    img_str=img_str.replace('#'+default.dark,'#CompletelyFakeStringToReplaceDark')
                if c.light != default.light:
                    img_str=img_str.replace('#'+default.light,'#'+c.light)
                if c.dark != default.dark:
                    img_str=img_str.replace('#CompletelyFakeStringToReplaceDark','#'+c.dark)
                self.svg  = PyQt6.QtSvg.QSvgRenderer(PyQt6.QtCore.QByteArray(img_str.encode()))
                self.image= PyQt6.QtGui.QImage(256,256, PyQt6.QtGui.QImage.Format.Format_ARGB32)
                self.svg.render(PyQt6.QtGui.QPainter(self.image))
                self.icon = PyQt6.QtGui.QIcon(PyQt6.QtGui.QPixmap.fromImage(self.image))
            except:
                self.psvg = ''
                self.id   = 'SP_MessageBoxQuestion'
                self.Build()
            return
        def GetId(self):
            return self.id
    def __init__(self,giftray):
        self.images = {}
        self.giftray= giftray
    def create(self,svg,letter,color):
        icon = self.singleIcon(self.giftray,svg,letter,color)
        if not icon.GetId() in self.images:
            icon.Build()
        if not icon.GetId() in self.images:
            self.images[icon.GetId()] =icon
        return (icon.GetId())
    def getIcon(self,id):
        if id in self.images:
            return self.images[id].icon
    def getPath(self,id):
        if id in self.images:
            return self.images[id].psvg
        
# def GetIcon(path,giftray,ico="default_default.ico"):
    # if not ico:
        # ico="default_default.ico"
    # last_try=False
    # if ico=="default_default.ico":
        # last_try=True
    # icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    # if ':' in ico:
        # iconPathName = os.path.abspath(ico).replace('\\','/')
    # else:
        # iconPathName = os.path.abspath(posixpath.join( path, ico )).replace('\\','/')
    # if os.path.isfile(iconPathName):
        # try:
            # standardIcon = PyQt6.QtGui.QIcon(iconPathName)
            # #hicon = win32gui.LoadImage(0, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
            # if standardIcon.availableSizes() != []:
                # return standardIcon, iconPathName
        # except:
            # pass
    # if not last_try:
        # return GetIcon(path,giftray)
    # #hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    # standardIcon = PyQt6.QtWidgets.QWidget().style().standardIcon(
                        # #PyQt6.QtWidgets.QStyle.StandardPixmap.SP_TitleBarContextHelpButton) #too dark
                        # PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion) #too dark
    # return standardIcon, ""
