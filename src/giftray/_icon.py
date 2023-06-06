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
        self.set('native'    ,'2ca9bc','000000')
        self.set('grey'      ,''      ,''      )
        self.set('darkgrey'  ,'AAAAAA','000000')
        self.set('black'     ,'000000','000000')
        self.set('white'     ,'FFFFFF',''      )
        self.set('darkwhite' ,'FFFFFF','000000')
        self.set('blue'      ,'1185E1','4DCFE1')
        self.set('darkblue'  ,'1185E1','000000')
        self.set('green'     ,'32CD32','7CFC00')
        self.set('darkgreen' ,'32CD32','000000')
        self.set('red'       ,'FDC75B','ED664C')
        self.set('darkred'   ,'ED664C','000000')
        self.set('darkyellow','FDC75B','000000')
        self.set('monowhite' ,'FFFFFF','FFFFFF')
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
            return self.colors["native"]
    def GetName(self,color):
        c = color.casefold()
        if color in self.colors:
            return c
        else:
            return 'native'
    def listThemes(self):
        a = []
        for c in self.colors:
            a.append(c)
        return a
    # def list(self):
        # for color in self.colors:
            # self.show(color)
        # print("End Colors")
    # def show(self,color):
            # print('color set:',color,self.colors[color].dark,self.colors[color].light)

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
        self.default=default()
    def create(self,svg,letter,theme,generic=''):
        icon = singleIcon(self.giftray,svg,letter,theme,generic,self.default)
        if not icon.GetId() in self.images:
            icon.Build()
        id = icon.GetId()
        if not id in self.images:
            self.images[id] =icon
        return (id)
    def getIcon(self,id):
        if id in self.images:
            return self.images[id].icon
    def getPath(self,id):
        if id in self.images:
            return self.images[id].psvg
    def getDefault(self):
        return self.default.getDefault()

class singleIcon:
    def __init__(self, giftray, svg, letter, theme, generic, default):
        self.default = default
        self.colors = giftray.colors
        self.theme = theme
        self.psvg = ""
        self.psvg = self._GetSVG(svg, letter, giftray.conf, generic)
        c = giftray.colors.get(theme)
        if not self.psvg:
            self.id = "SP_MessageBoxQuestion"
        else:
            self.id=self.psvg+'/'+c.dark+'/'+c.light
        if generic and not self.psvg:
            self.psvg = generic
            self.id   = self.psvg+'/'+c.dark+'/'+c.light
            if svg or letter:
                giftray.main_error.append("Fail to find '"+generic.split('_')[1]+"' icon")

    def _GetSVG(self,svg,letter,conf,generic):
        psvgs=[]
        if svg:
            psvg = os.path.abspath(svg)
            if os.path.exists(psvg) and psvg.endswith('.svg'):
                return(psvg)
            if not svg.endswith('.svg'):
                psvgs.append('icons/'+svg+'.svg')
            else:
                psvgs.append('icons/'+svg)
        if letter and len(letter)==1 and letter in 'abcdefghijklmnopqrstuvwxyz1234567890':
            psvgs.append('letters/'+letter.casefold()+'.svg')
        elif not generic or not generic in self.default.getDefault() :
            psvgs.append('letters/number-circle-fill.svg')
        arrpath = []
        if not '\\python' in sys.executable:
            arrpath.append(os.path.dirname(sys.executable))
        arrpath.append(os.path.dirname(conf))
        arrpath.append(os.getcwd())
        for psvg in psvgs:
            for thispath in arrpath:
                for endpath in [['svg'],['src','svg']]:
                    path = thispath
                    for k in endpath:
                        path = posixpath.join(path,k)
                    path = os.path.abspath(posixpath.join( path, psvg))
                    if os.path.exists(path):
                        return(path)
        return("")

    def Build(self):
        if (not self.psvg or self.id == 'SP_MessageBoxQuestion') and not self.id.startswith('GENERIC_'):
            self.id   = 'SP_MessageBoxQuestion'
            self.psvg = ''
            self.icon = PyQt6.QtWidgets.QWidget().style().standardIcon(
                            #PyQt6.QtWidgets.QStyle.StandardPixmap.SP_TitleBarContextHelpButton) #too dark
                            PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion) #too dark
            return
        try:
            if self.id.startswith('GENERIC_'):
                img_str = self.default.get(self.psvg)
            else:
                with open(self.psvg, 'r') as file:
                    img_str = file.read()
            c = self.colors.get(self.theme)
            native = self.colors.get('native')
            if c.dark != native.dark:
                img_str=img_str.replace('#'+native.dark,'#CompletelyFakeStringToReplaceDark')
            if c.light != native.light:
                img_str=img_str.replace('#'+native.light,'#'+c.light)
            if c.dark != native.dark:
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

class default:
    def __init__(self):
        self.default = []
        self.img_str = dict()
        #self.img_str['GENERIC_Main']='<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill="#2ca9bc" d="M5 10H19V20H5V10Z"/><path fill="#2ca9bc" d="M4 7H20V10H4V7Z"/><path fill="#000000" d="M5 9.99999V9.24999C4.58579 9.24999 4.25 9.58578 4.25 9.99999H5ZM19 9.99999H19.75C19.75 9.58578 19.4142 9.24999 19 9.24999V9.99999ZM19 20V20.75C19.4142 20.75 19.75 20.4142 19.75 20H19ZM5 20H4.25C4.25 20.4142 4.58579 20.75 5 20.75V20ZM14 20V20.75C14.4142 20.75 14.75 20.4142 14.75 20H14ZM10 20H9.25C9.25 20.4142 9.58579 20.75 10 20.75V20ZM4 6.99999V6.24999C3.58579 6.24999 3.25 6.58578 3.25 6.99999H4ZM20 6.99999H20.75C20.75 6.58578 20.4142 6.24999 20 6.24999V6.99999ZM20 9.99999V10.75C20.4142 10.75 20.75 10.4142 20.75 9.99999H20ZM4 9.99999H3.25C3.25 10.4142 3.58579 10.75 4 10.75V9.99999ZM10 6.99999V6.24999C9.58579 6.24999 9.25 6.58578 9.25 6.99999H10ZM14 6.99999H14.75C14.75 6.58578 14.4142 6.24999 14 6.24999V6.99999ZM11.8659 6.84997L11.1415 6.65582L10.9473 7.38026L11.6718 7.57441L11.8659 6.84997ZM17.0621 3.84997L17.7116 3.47497L17.7116 3.47497L17.0621 3.84997ZM12.0623 6.84997L12.2565 7.57441L12.9809 7.38026L12.7868 6.65582L12.0623 6.84997ZM6.86617 3.84997L6.21665 3.47497L6.21665 3.47497L6.86617 3.84997ZM5 10.75H19V9.24999H5V10.75ZM18.25 9.99999V20H19.75V9.99999H18.25ZM19 19.25H5V20.75H19V19.25ZM5.75 20V9.99999H4.25V20H5.75ZM10 10.75H14V9.24999H10V10.75ZM13.25 9.99999V20H14.75V9.99999H13.25ZM14 19.25H10V20.75H14V19.25ZM10.75 20V9.99999H9.25V20H10.75ZM4 7.74999H20V6.24999H4V7.74999ZM19.25 6.99999V9.99999H20.75V6.99999H19.25ZM20 9.24999H4V10.75H20V9.24999ZM4.75 9.99999V6.99999H3.25V9.99999H4.75ZM10 7.74999H14V6.24999H10V7.74999ZM13.25 6.99999V9.99999H14.75V6.99999H13.25ZM10.75 9.99999V6.99999H9.25V9.99999H10.75ZM12.5903 7.04412C12.8189 6.19124 13.6426 4.92567 14.5705 4.19729C15.0346 3.83294 15.4228 3.68419 15.6937 3.68451C15.8907 3.68474 16.1444 3.76048 16.4125 4.22497L17.7116 3.47497C17.2297 2.64039 16.5275 2.18549 15.6954 2.18451C14.9372 2.18362 14.223 2.56308 13.6443 3.01739C12.4864 3.92631 11.462 5.45979 11.1415 6.65582L12.5903 7.04412ZM16.4125 4.22497C16.6807 4.6895 16.6195 4.94712 16.5212 5.11788C16.386 5.35264 16.0631 5.61443 15.5156 5.83422C14.4208 6.27363 12.913 6.35413 12.0601 6.12554L11.6718 7.57441C12.8679 7.89498 14.7082 7.7746 16.0743 7.22627C16.7571 6.9522 17.4428 6.52341 17.8211 5.86628C18.2363 5.14515 18.1934 4.30956 17.7116 3.47497L16.4125 4.22497ZM12.7868 6.65582C12.4662 5.45979 11.4418 3.92631 10.2839 3.01739C9.70518 2.56308 8.99101 2.18362 8.23278 2.18451C7.40069 2.18549 6.69849 2.64039 6.21665 3.47497L7.51569 4.22497C7.78386 3.76048 8.03754 3.68474 8.23455 3.68451C8.50543 3.68419 8.89359 3.83294 9.35773 4.19729C10.2856 4.92567 11.1093 6.19124 11.3379 7.04412L12.7868 6.65582ZM6.21665 3.47497C5.7348 4.30956 5.69191 5.14515 6.10708 5.86628C6.48539 6.52341 7.17109 6.9522 7.85392 7.22627C9.22001 7.7746 11.0603 7.89498 12.2565 7.57441L11.8682 6.12554C11.0152 6.35413 9.50739 6.27363 8.41266 5.83422C7.86508 5.61443 7.54219 5.35264 7.40704 5.11788C7.30873 4.94712 7.24749 4.6895 7.51569 4.22497L6.21665 3.47497Z"/></svg>'
        self.img_str['GENERIC_Exit']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="sign-out" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M14.56,18.35,13,17.05a1,1,0,0,1-.11-1.41L14.34,14H7V10h7.34L12.93,8.36A1,1,0,0,1,13,7l1.52-1.3A1,1,0,0,1,16,5.76l4.79,5.59a1,1,0,0,1,0,1.3L16,18.24A1,1,0,0,1,14.56,18.35Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M7,20H4a1,1,0,0,1-1-1V5A1,1,0,0,1,4,4H7" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M14.56,18.35,13,17.05a1,1,0,0,1-.11-1.41L14.34,14H7V10h7.34L12.93,8.36A1,1,0,0,1,13,7l1.52-1.3A1,1,0,0,1,16,5.76l4.79,5.59a1,1,0,0,1,0,1.3L16,18.24A1,1,0,0,1,14.56,18.35Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
        self.img_str['GENERIC_Errors']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="warning-alt" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M10.25,4.19,2.63,18a2,2,0,0,0,1.75,3H19.62a2,2,0,0,0,1.75-3L13.75,4.19A2,2,0,0,0,10.25,4.19Z" style="fill:#2ca9bc; stroke-width: 2;"></path><line id="primary-upstroke" x1="12.05" y1="17" x2="11.95" y2="17" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5;"></line><path id="primary" d="M12,9v4M10.25,4.19,2.63,18a2,2,0,0,0,1.75,3H19.62a2,2,0,0,0,1.75-3L13.75,4.19A2,2,0,0,0,10.25,4.19Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
        self.img_str['GENERIC_Reload']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="exchange-5" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M7,3a4,4,0,1,0,4,4A4,4,0,0,0,7,3ZM17,21a4,4,0,1,0-4-4A4,4,0,0,0,17,21Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M14.57,4.43a8,8,0,0,1,3.09,1.91,8.13,8.13,0,0,1,2,3.3" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><polyline id="primary-2" data-name="primary" points="17.85 8.81 19.66 9.65 20.5 7.84" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></polyline><path id="primary-3" data-name="primary" d="M4.35,14.36a8.13,8.13,0,0,0,2,3.3,8,8,0,0,0,3.09,1.91" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><polyline id="primary-4" data-name="primary" points="6.15 15.19 4.34 14.35 3.5 16.16" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></polyline><path id="primary-5" data-name="primary" d="M7,3a4,4,0,1,0,4,4A4,4,0,0,0,7,3ZM17,21a4,4,0,1,0-4-4A4,4,0,0,0,17,21Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
        self.img_str['GENERIC_No-Click']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="decrease-circle" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><circle id="secondary" cx="12" cy="12" r="9" style="fill:#2ca9bc; stroke-width: 2;"></circle><path id="primary" d="M7.76,12h8.48M12,3a9,9,0,1,0,9,9A9,9,0,0,0,12,3Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
        self.img_str['GENERIC_Menu']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="add-collection" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><rect id="secondary" x="3" y="3" width="14" height="14" rx="1" style="fill:#2ca9bc; stroke-width: 2;"></rect><path id="primary" d="M7,21H20a1,1,0,0,0,1-1V5" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M7,10h6M10,7v6m7,3V4a1,1,0,0,0-1-1H4A1,1,0,0,0,3,4V16a1,1,0,0,0,1,1H16A1,1,0,0,0,17,16Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
        self.img_str['GENERIC_About']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="chat-alert-left" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M3,11c0-4.42,4-8,9-8s9,3.58,9,8-4,8-9,8A9.87,9.87,0,0,1,9,18.52L4,21l1.19-4.77A7.5,7.5,0,0,1,3,11Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M3,11c0-4.42,4-8,9-8s9,3.58,9,8-4,8-9,8A9.87,9.87,0,0,1,9,18.52L4,21l1.19-4.77A7.5,7.5,0,0,1,3,11Zm9-4v3" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><line id="primary-upstroke" x1="12.05" y1="14.5" x2="11.95" y2="14.5" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5;"></line></svg>'
        self.img_str['GENERIC_Tray']='<?xml version="1.0" encoding="iso-8859-1"?><svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 456.098 456.098" style="enable-background:new 0 0 456.098 456.098;" xml:space="preserve"><path style="fill:#000000;" d="M309.029,0c-41.273,0-66.873,31.347-80.98,58.514C213.943,31.347,188.343,0,147.069,0 c-31.347,0-56.424,26.122-56.424,57.992c0,32.392,25.078,59.037,56.424,59.037V85.682c-13.584,0-25.078-12.539-25.078-27.69 c0-14.629,11.494-26.645,25.078-26.645c47.02,0,65.829,72.62,65.829,73.143l15.151-3.657l15.151,3.657 c0-0.522,18.808-73.143,65.829-73.143c13.584,0,25.078,12.016,25.078,26.645c0,15.151-11.494,27.69-25.078,27.69v31.347 c31.347,0,56.424-26.645,56.424-59.037C365.453,26.122,340.375,0,309.029,0z"/><rect x="243.722" y="101.355" style="fill:#000000;" width="31.347" height="339.069"/><rect x="181.029" y="101.355" style="fill:#000000;" width="31.347" height="339.069"/><path style="fill:#2ca9bc;" d="M430.237,85.682H25.861c-8.882,0-15.673,6.792-15.673,15.673v99.788 c0,8.882,6.792,15.673,15.673,15.673h10.971v223.608c0,8.882,6.792,15.673,15.673,15.673h351.086 c8.882,0,15.673-6.792,15.673-15.673V216.816h10.971c8.882,0,15.673-6.792,15.673-15.673v-99.788 C445.91,92.473,439.118,85.682,430.237,85.682z M41.535,117.029h373.029v68.441H41.535V117.029z M387.918,424.751H68.18V216.816 h319.739V424.751z"/></svg>'
        self.img_str['GENERIC_Generator']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="edit-alt-2" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><polygon id="secondary" points="10.47 9.29 14.71 13.53 7.24 21 3 21 3 16.76 10.47 9.29" style="fill:#2ca9bc; stroke-width: 2;"></polygon><path id="primary" d="M20.41,7.83l-2.88,2.88L13.29,6.47l2.88-2.88a1,1,0,0,1,1.42,0l2.82,2.82A1,1,0,0,1,20.41,7.83ZM3,16.76V21H7.24l7.47-7.47L10.47,9.29Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
        self.img_str['GENERIC_Configuration']='<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="settings" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M20,10h-.59a1,1,0,0,1-.94-.67v0a1,1,0,0,1,.2-1.14l.41-.41a1,1,0,0,0,0-1.42L17.66,4.93a1,1,0,0,0-1.42,0l-.41.41a1,1,0,0,1-1.14.2h0A1,1,0,0,1,14,4.59V4a1,1,0,0,0-1-1H11a1,1,0,0,0-1,1v.59a1,1,0,0,1-.67.94h0a1,1,0,0,1-1.14-.2l-.41-.41a1,1,0,0,0-1.42,0L4.93,6.34a1,1,0,0,0,0,1.42l.41.41a1,1,0,0,1,.2,1.14v0a1,1,0,0,1-.94.67H4a1,1,0,0,0-1,1v2a1,1,0,0,0,1,1h.59a1,1,0,0,1,.94.67v0a1,1,0,0,1-.2,1.14l-.41.41a1,1,0,0,0,0,1.42l1.41,1.41a1,1,0,0,0,1.42,0l.41-.41a1,1,0,0,1,1.14-.2h0a1,1,0,0,1,.67.94V20a1,1,0,0,0,1,1h2a1,1,0,0,0,1-1v-.59a1,1,0,0,1,.67-.94h0a1,1,0,0,1,1.14.2l.41.41a1,1,0,0,0,1.42,0l1.41-1.41a1,1,0,0,0,0-1.42l-.41-.41a1,1,0,0,1-.2-1.14v0a1,1,0,0,1,.94-.67H20a1,1,0,0,0,1-1V11A1,1,0,0,0,20,10Zm-8,5a3,3,0,1,1,3-3A3,3,0,0,1,12,15Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M15,12a3,3,0,1,1-3-3A3,3,0,0,1,15,12Zm5-2h-.59a1,1,0,0,1-.94-.67v0a1,1,0,0,1,.2-1.14l.41-.41a1,1,0,0,0,0-1.42L17.66,4.93a1,1,0,0,0-1.42,0l-.41.41a1,1,0,0,1-1.14.2h0A1,1,0,0,1,14,4.59V4a1,1,0,0,0-1-1H11a1,1,0,0,0-1,1v.59a1,1,0,0,1-.67.94h0a1,1,0,0,1-1.14-.2l-.41-.41a1,1,0,0,0-1.42,0L4.93,6.34a1,1,0,0,0,0,1.42l.41.41a1,1,0,0,1,.2,1.14v0a1,1,0,0,1-.94.67H4a1,1,0,0,0-1,1v2a1,1,0,0,0,1,1h.59a1,1,0,0,1,.94.67v0a1,1,0,0,1-.2,1.14l-.41.41a1,1,0,0,0,0,1.42l1.41,1.41a1,1,0,0,0,1.42,0l.41-.41a1,1,0,0,1,1.14-.2h0a1,1,0,0,1,.67.94V20a1,1,0,0,0,1,1h2a1,1,0,0,0,1-1v-.59a1,1,0,0,1,.67-.94h0a1,1,0,0,1,1.14.2l.41.41a1,1,0,0,0,1.42,0l1.41-1.41a1,1,0,0,0,0-1.42l-.41-.41a1,1,0,0,1-.2-1.14v0a1,1,0,0,1,.94-.67H20a1,1,0,0,0,1-1V11A1,1,0,0,0,20,10Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
        self.img_str['GENERIC_Help']='<?xml version="1.0" encoding="utf-8"?> <svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="help" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M10.91,8.16,9.53,3.35A9,9,0,0,0,3.35,9.53l4.81,1.38A4,4,0,0,1,10.91,8.16ZM8.16,13.09,3.35,14.47a9,9,0,0,0,6.18,6.18l1.38-4.81A4,4,0,0,1,8.16,13.09Zm6.31-9.74L13.09,8.16a4,4,0,0,1,2.75,2.75l4.81-1.38A9,9,0,0,0,14.47,3.35Zm1.37,9.74a4,4,0,0,1-2.75,2.75l1.38,4.81a9,9,0,0,0,6.18-6.18Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M20.42,14.41,16.1,13.17m4.32-3.58L16.1,10.83M3.58,9.59,7.9,10.83M3.58,14.41,7.9,13.17m1.69,7.25,1.24-4.32m2.34,0,1.24,4.32m0-16.84L13.17,7.9m-2.34,0L9.59,3.58M12,3a9,9,0,1,0,9,9A9,9,0,0,0,12,3Zm0,5a4,4,0,1,0,4,4A4,4,0,0,0,12,8Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'
    def getDefault(self):
        if not self.default:
            for i in self.img_str:
                #self.default.append(i.split('_')[1])
                self.default.append(i)
        return self.default
    def get(self,g):
        return self.img_str[g]
