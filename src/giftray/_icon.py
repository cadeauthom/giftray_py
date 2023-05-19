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

class svgIcons:
    def __init__(self,giftray):
        self.images = {}
        self.giftray= giftray
        self.generic=generic()
    def create(self,svg,letter,theme,generic=''):
        icon = singleIcon(self.giftray,svg,letter,theme,generic)
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
    def default(self):
        return self.generic.getGeneric()

class singleIcon:
    def __init__(self,giftray, svg, letter, theme, generic):
        self.colors = giftray.colors
        self.theme = theme
        self.generic = generic
        if self.generic:
            self.psvg = 'GENERIC'
            self.id   = 'GENERIC_'+generic
        else:
            self.psvg = self._GetSVG(svg,letter,giftray.conf)
            if not self.psvg:
                self.id = "SP_MessageBoxQuestion"
            else:
                c = giftray.colors.get(theme)
                self.id=self.psvg+'/'+c.dark+'/'+c.light
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
    def Build(self):
        if not self.psvg or self.id == 'SP_MessageBoxQuestion':
            self.id   = 'SP_MessageBoxQuestion'
            self.psvg = ''
            self.icon = PyQt6.QtWidgets.QWidget().style().standardIcon(
                            #PyQt6.QtWidgets.QStyle.StandardPixmap.SP_TitleBarContextHelpButton) #too dark
                            PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion) #too dark
            return
        try:
            if self.id.startswith('GENERIC_'):
                img_str = generic.get(self.id)
            else:
                with open(self.psvg, 'r') as file:
                    img_str = file.read()
            c = self.colors.get(self.theme)
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
            #not svg:
                # icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                # standardIcon = PyQt6.QtGui.QIcon(iconPathName)
                # #hicon = win32gui.LoadImage(0, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
                # if standardIcon.availableSizes() != []:
                    # return standardIcon, iconPathName
        except:
            self.psvg = ''
            self.id   = 'SP_MessageBoxQuestion'
            self.Build()
        return
    def GetId(self):
        return self.id

class generic:
    def __init__(self):
        self.generic = []
        self.img_str = dict()
        self.img_str['GENERIC_menu']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="add-collection" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><rect id="secondary" x="3" y="3" width="14" height="14" rx="1" style="fill:#2ca9bc; stroke-width: 2;"></rect><path id="primary" d="M7,21H20a1,1,0,0,0,1-1V5" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M7,10h6M10,7v6m7,3V4a1,1,0,0,0-1-1H4A1,1,0,0,0,3,4V16a1,1,0,0,0,1,1H16A1,1,0,0,0,17,16Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
    def getGeneric(self):
        if not self.generic:
            for i in self.img_str:
                self.generic.append(i.split('_')[1])
        return self.generic
