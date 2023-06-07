import os
import sys
import shutil
import trace, threading
import win32con
import win32api
import win32process
try:
    import win32gui
except ImportError:
    import winxpgui as win32gui
import enum
import re

class type(enum.Enum):
    UINT        = 1
    INT         = 2
    BOOL        = 3
    STRING      = 4
    LOWSTRING   = 5
    UPSTRING    = 6
    LISTSTRING  = 7
    PATH        = 8
    COLOR       = 9
    THEME       = 10

class trayconf:
    def __init__(self):
        #Init Internal
        self.internal = dict()
        self.internal['Icons'] = {
                        'GENERIC_Tray'      :'<?xml version="1.0" encoding="iso-8859-1"?><svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 456.098 456.098" style="enable-background:new 0 0 456.098 456.098;" xml:space="preserve"><path style="fill:#000000;" d="M309.029,0c-41.273,0-66.873,31.347-80.98,58.514C213.943,31.347,188.343,0,147.069,0 c-31.347,0-56.424,26.122-56.424,57.992c0,32.392,25.078,59.037,56.424,59.037V85.682c-13.584,0-25.078-12.539-25.078-27.69 c0-14.629,11.494-26.645,25.078-26.645c47.02,0,65.829,72.62,65.829,73.143l15.151-3.657l15.151,3.657 c0-0.522,18.808-73.143,65.829-73.143c13.584,0,25.078,12.016,25.078,26.645c0,15.151-11.494,27.69-25.078,27.69v31.347 c31.347,0,56.424-26.645,56.424-59.037C365.453,26.122,340.375,0,309.029,0z"/><rect x="243.722" y="101.355" style="fill:#000000;" width="31.347" height="339.069"/><rect x="181.029" y="101.355" style="fill:#000000;" width="31.347" height="339.069"/><path style="fill:#2ca9bc;" d="M430.237,85.682H25.861c-8.882,0-15.673,6.792-15.673,15.673v99.788 c0,8.882,6.792,15.673,15.673,15.673h10.971v223.608c0,8.882,6.792,15.673,15.673,15.673h351.086 c8.882,0,15.673-6.792,15.673-15.673V216.816h10.971c8.882,0,15.673-6.792,15.673-15.673v-99.788 C445.91,92.473,439.118,85.682,430.237,85.682z M41.535,117.029h373.029v68.441H41.535V117.029z M387.918,424.751H68.18V216.816 h319.739V424.751z"/></svg>',
                        'GENERIC_Errors'    :'<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="warning-alt" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M10.25,4.19,2.63,18a2,2,0,0,0,1.75,3H19.62a2,2,0,0,0,1.75-3L13.75,4.19A2,2,0,0,0,10.25,4.19Z" style="fill:#2ca9bc; stroke-width: 2;"></path><line id="primary-upstroke" x1="12.05" y1="17" x2="11.95" y2="17" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5;"></line><path id="primary" d="M12,9v4M10.25,4.19,2.63,18a2,2,0,0,0,1.75,3H19.62a2,2,0,0,0,1.75-3L13.75,4.19A2,2,0,0,0,10.25,4.19Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>',
                        'GENERIC_Exit'      :'<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="sign-out" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M14.56,18.35,13,17.05a1,1,0,0,1-.11-1.41L14.34,14H7V10h7.34L12.93,8.36A1,1,0,0,1,13,7l1.52-1.3A1,1,0,0,1,16,5.76l4.79,5.59a1,1,0,0,1,0,1.3L16,18.24A1,1,0,0,1,14.56,18.35Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M7,20H4a1,1,0,0,1-1-1V5A1,1,0,0,1,4,4H7" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M14.56,18.35,13,17.05a1,1,0,0,1-.11-1.41L14.34,14H7V10h7.34L12.93,8.36A1,1,0,0,1,13,7l1.52-1.3A1,1,0,0,1,16,5.76l4.79,5.59a1,1,0,0,1,0,1.3L16,18.24A1,1,0,0,1,14.56,18.35Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>',
                        'GENERIC_Reload'    :'<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="exchange-5" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M7,3a4,4,0,1,0,4,4A4,4,0,0,0,7,3ZM17,21a4,4,0,1,0-4-4A4,4,0,0,0,17,21Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M14.57,4.43a8,8,0,0,1,3.09,1.91,8.13,8.13,0,0,1,2,3.3" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><polyline id="primary-2" data-name="primary" points="17.85 8.81 19.66 9.65 20.5 7.84" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></polyline><path id="primary-3" data-name="primary" d="M4.35,14.36a8.13,8.13,0,0,0,2,3.3,8,8,0,0,0,3.09,1.91" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><polyline id="primary-4" data-name="primary" points="6.15 15.19 4.34 14.35 3.5 16.16" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></polyline><path id="primary-5" data-name="primary" d="M7,3a4,4,0,1,0,4,4A4,4,0,0,0,7,3ZM17,21a4,4,0,1,0-4-4A4,4,0,0,0,17,21Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>',
                        'GENERIC_No-Click'  :'<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="decrease-circle" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><circle id="secondary" cx="12" cy="12" r="9" style="fill:#2ca9bc; stroke-width: 2;"></circle><path id="primary" d="M7.76,12h8.48M12,3a9,9,0,1,0,9,9A9,9,0,0,0,12,3Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>',
                        'GENERIC_Menu'      :'<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="add-collection" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><rect id="secondary" x="3" y="3" width="14" height="14" rx="1" style="fill:#2ca9bc; stroke-width: 2;"></rect><path id="primary" d="M7,21H20a1,1,0,0,0,1-1V5" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M7,10h6M10,7v6m7,3V4a1,1,0,0,0-1-1H4A1,1,0,0,0,3,4V16a1,1,0,0,0,1,1H16A1,1,0,0,0,17,16Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>',
                        'GENERIC_About'     :'<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="chat-alert-left" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M3,11c0-4.42,4-8,9-8s9,3.58,9,8-4,8-9,8A9.87,9.87,0,0,1,9,18.52L4,21l1.19-4.77A7.5,7.5,0,0,1,3,11Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M3,11c0-4.42,4-8,9-8s9,3.58,9,8-4,8-9,8A9.87,9.87,0,0,1,9,18.52L4,21l1.19-4.77A7.5,7.5,0,0,1,3,11Zm9-4v3" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><line id="primary-upstroke" x1="12.05" y1="14.5" x2="11.95" y2="14.5" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5;"></line></svg>',
                        'GENERIC_Generator' :'<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="edit-alt-2" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><polygon id="secondary" points="10.47 9.29 14.71 13.53 7.24 21 3 21 3 16.76 10.47 9.29" style="fill:#2ca9bc; stroke-width: 2;"></polygon><path id="primary" d="M20.41,7.83l-2.88,2.88L13.29,6.47l2.88-2.88a1,1,0,0,1,1.42,0l2.82,2.82A1,1,0,0,1,20.41,7.83ZM3,16.76V21H7.24l7.47-7.47L10.47,9.29Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>',
                        'GENERIC_Help'      :'<?xml version="1.0" encoding="utf-8"?> <svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="help" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M10.91,8.16,9.53,3.35A9,9,0,0,0,3.35,9.53l4.81,1.38A4,4,0,0,1,10.91,8.16ZM8.16,13.09,3.35,14.47a9,9,0,0,0,6.18,6.18l1.38-4.81A4,4,0,0,1,8.16,13.09Zm6.31-9.74L13.09,8.16a4,4,0,0,1,2.75,2.75l4.81-1.38A9,9,0,0,0,14.47,3.35Zm1.37,9.74a4,4,0,0,1-2.75,2.75l1.38,4.81a9,9,0,0,0,6.18-6.18Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M20.42,14.41,16.1,13.17m4.32-3.58L16.1,10.83M3.58,9.59,7.9,10.83M3.58,14.41,7.9,13.17m1.69,7.25,1.24-4.32m2.34,0,1.24,4.32m0-16.84L13.17,7.9m-2.34,0L9.59,3.58M12,3a9,9,0,1,0,9,9A9,9,0,0,0,12,3Zm0,5a4,4,0,1,0,4,4A4,4,0,0,0,12,8Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>',
                        'GENERIC_Configuration':'<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="settings" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M20,10h-.59a1,1,0,0,1-.94-.67v0a1,1,0,0,1,.2-1.14l.41-.41a1,1,0,0,0,0-1.42L17.66,4.93a1,1,0,0,0-1.42,0l-.41.41a1,1,0,0,1-1.14.2h0A1,1,0,0,1,14,4.59V4a1,1,0,0,0-1-1H11a1,1,0,0,0-1,1v.59a1,1,0,0,1-.67.94h0a1,1,0,0,1-1.14-.2l-.41-.41a1,1,0,0,0-1.42,0L4.93,6.34a1,1,0,0,0,0,1.42l.41.41a1,1,0,0,1,.2,1.14v0a1,1,0,0,1-.94.67H4a1,1,0,0,0-1,1v2a1,1,0,0,0,1,1h.59a1,1,0,0,1,.94.67v0a1,1,0,0,1-.2,1.14l-.41.41a1,1,0,0,0,0,1.42l1.41,1.41a1,1,0,0,0,1.42,0l.41-.41a1,1,0,0,1,1.14-.2h0a1,1,0,0,1,.67.94V20a1,1,0,0,0,1,1h2a1,1,0,0,0,1-1v-.59a1,1,0,0,1,.67-.94h0a1,1,0,0,1,1.14.2l.41.41a1,1,0,0,0,1.42,0l1.41-1.41a1,1,0,0,0,0-1.42l-.41-.41a1,1,0,0,1-.2-1.14v0a1,1,0,0,1,.94-.67H20a1,1,0,0,0,1-1V11A1,1,0,0,0,20,10Zm-8,5a3,3,0,1,1,3-3A3,3,0,0,1,12,15Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M15,12a3,3,0,1,1-3-3A3,3,0,0,1,15,12Zm5-2h-.59a1,1,0,0,1-.94-.67v0a1,1,0,0,1,.2-1.14l.41-.41a1,1,0,0,0,0-1.42L17.66,4.93a1,1,0,0,0-1.42,0l-.41.41a1,1,0,0,1-1.14.2h0A1,1,0,0,1,14,4.59V4a1,1,0,0,0-1-1H11a1,1,0,0,0-1,1v.59a1,1,0,0,1-.67.94h0a1,1,0,0,1-1.14-.2l-.41-.41a1,1,0,0,0-1.42,0L4.93,6.34a1,1,0,0,0,0,1.42l.41.41a1,1,0,0,1,.2,1.14v0a1,1,0,0,1-.94.67H4a1,1,0,0,0-1,1v2a1,1,0,0,0,1,1h.59a1,1,0,0,1,.94.67v0a1,1,0,0,1-.2,1.14l-.41.41a1,1,0,0,0,0,1.42l1.41,1.41a1,1,0,0,0,1.42,0l.41-.41a1,1,0,0,1,1.14-.2h0a1,1,0,0,1,.67.94V20a1,1,0,0,0,1,1h2a1,1,0,0,0,1-1v-.59a1,1,0,0,1,.67-.94h0a1,1,0,0,1,1.14.2l.41.41a1,1,0,0,0,1.42,0l1.41-1.41a1,1,0,0,0,0-1.42l-.41-.41a1,1,0,0,1-.2-1.14v0a1,1,0,0,1,.94-.67H20a1,1,0,0,0,1-1V11A1,1,0,0,0,20,10Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>',
                        }
        self.internal['Themes'] = {
                        'Native':       {'Dark': '2ca9bc', 'Light': '000000'},
                        'Grey':         {'Dark': '000000', 'Light': 'AAAAAA'},
                        'DarkGrey':     {'Dark': 'AAAAAA', 'Light': '000000'},
                        'Black':        {'Dark': '000000', 'Light': '000000'},
                        'White':        {'Dark': 'FFFFFF', 'Light': 'AAAAAA'},
                        'DarkWhite':    {'Dark': 'FFFFFF', 'Light': '000000'},
                        'Blue':         {'Dark': '1185E1', 'Light': '4DCFE1'},
                        'DarkBlue':     {'Dark': '1185E1', 'Light': '000000'},
                        'Green':        {'Dark': '32CD32', 'Light': '7CFC00'},
                        'DarkGreen':    {'Dark': '32CD32', 'Light': '000000'},
                        'Red':          {'Dark': 'FDC75B', 'Light': 'ED664C'},
                        'DarkRed':      {'Dark': 'ED664C', 'Light': '000000'},
                        'DarkYellow':   {'Dark': 'FDC75B', 'Light': '000000'},
                        'MonoWhite':    {'Dark': 'FFFFFF', 'Light': 'FFFFFF'}
                        }
        #Init Conf
        self.conf = dict()
        self.conf['Generals'] = dict()
        self.conf['Folders'] = dict()
        self.conf['Actions'] = dict()
        self.conf['Generals']['LogLevel'] = "WARNING"
        self.conf['Generals']['Silent'] = False
        self.conf['Generals']['Icons'] = dict()
        self.conf['Generals']['Themes'] = {
                        'Tray'   : {'Theme': 'MonoWhite',
                                    'Dark':  '',
                                    'Light': ''},
                        'Default': {'Theme': 'Native',
                                    'Dark':  '',
                                    'Light': ''},
                        'Custom' : {'Theme': 'Native',
                                    'Dark':  '',
                                    'Light': ''}}
        for i in self.internal['Icons']:
            k = i
            if i.startswith('GENERIC_'):
                k = i[len('GENERIC_'):]
            self.conf['Generals']['Icons'][k] = None
    def getGeneral(self, module, key):
        if module in self.conf['Generals'] and key in self.conf['Generals'][module]:
            return self.conf['Generals'][module][key]
        return None
    def addConf(self, type, name, args):
        if not type or not name or not args:
            return
        if not type in self.conf:
            return
        if name in self.conf[type]:
            print("Update")
        self.conf[type][name] = args
    def updateTheme(self, theme, field, value):
        if not theme in self.conf['Generals']['Themes']:
            return
        if not field in self.conf['Generals']['Themes'][theme]:
            return
        self.conf['Generals']['Themes'][theme][field]=value
    def isInTray(self, section):
        return (section in self.conf['Folders']) or (section in self.conf['Actions'])
    def setIco(self, name, path):
        if name in self.conf['Generals']['Icons'] and path:
            self.conf['Generals']['Icons'][name] = path
    def setOpt(self, opt, value):
        if opt in self.conf['Generals']:
            self.conf['Generals'][opt] = value
    def print(self):
        self.write('pop')
    def write(self,path):
        import json
        json_object = json.dumps(self.conf, indent = 2)
        print(json_object)
        # json_object = json.dumps(self.internal, indent = 2)
        # print(json_object)

class mainmenuconf:
    def __init__(self,colors,images):
        self.colors = colors
        self.images = images
        self.themes = { 'tray'   : {'theme': 'monowhite',
                                    'dark': '',
                                    'light': ''},
                        'default': {'theme': 'native',
                                    'dark': '',
                                    'light': ''},
                        'other'  : {'theme': 'native',
                                    'dark': '',
                                    'light': ''}}
        self.icos   = dict()
        self.ids    = dict()
    def build(self):
        for theme in self.themes:
            self.colors.copy(self.themes[theme]['theme'],theme)
            self.colors.set(theme,self.themes[theme]['dark'],self.themes[theme]['light'])
        for ico in self.images.getDefault():
            pico = ""
            if ico in self.icos:
                pico = self.icos[ico]
            theme = 'default'
            if ico == 'GENERIC_'+'Tray'.title():
                theme = 'tray'
            id = self.images.create(pico,'',theme,generic=ico)
            self.ids[ico] = id
    def getIcon(self,id):
        if 'GENERIC_'+id.title() in self.ids:
            return self.images.getIcon(self.ids['GENERIC_'+id.title()])
    def set(self, theme, field, value):
        if not theme in self.themes:
            return
        if not field in self.themes[theme]:
            return
        self.themes[theme][field] = value

def GetOpt(val,t):
    ret = None
    if t == type.UINT:
        try:
            ret = abs(int(val))
        except:
            ret = 0
    elif t == type.INT:
        try:
            ret = int(val)
        except:
            ret = 0
    elif t == type.BOOL:
        try:
            if not val:
                ret = True
            else:
                ret = (str(val).title() in ['True'.title(),'On'.title(),'1'.title()])
        except:
            ret = False
    elif t == type.STRING:
        try:
            if not val:
                ret = ''
            else:
                ret = str(val)
        except:
            ret = ''
    elif t == type.LOWSTRING:
        try:
            if val == None:
                ret = ''
            else:
                ret = str(val).casefold()
        except:
            ret = ''
    elif t == type.UPSTRING:
        try:
            if val == None:
                ret = ''
            else:
                ret = str(val).upper()
        except:
            ret = ''
    elif t == type.LISTSTRING:
        try:
            ret = re.split('\s*[,;]\s*',val)
        except:
            ret = []
    elif t == type.PATH: #no subpath management, no icon path
        ret = WindowsHandler().GetRealPath(str(val))
    elif t == type.COLOR:
        ret = str(val).upper()
        if re.fullmatch(r"^[0-9a-fA-F]{6}$", ret) is not None:
            ret = '000000'
    elif t == type.THEME:
        ret = giftray.colors.GetName(str(t))
    return ret

class WindowsHandler():
    def __init__(self):
        self.global_array = []

    def _callback_enumChildWindows(self,handle, arg):
        if win32gui.GetClassName(handle) == arg:
            self.global_array.append(handle)
        return True
    def GetCurrentPath(self):
        hwnd      = win32gui.GetForegroundWindow()
        classname = win32gui.GetClassName(hwnd)
        #other windows: test if windows name contains a path
        full_text = (win32gui.GetWindowText(hwnd)).split()
        for idx, t in enumerate(full_text):
            if not(len(t)>3 and t[1]==':'):
                continue
            for i in range (len(full_text),idx,-1):
                text = ' '.join(full_text[idx:i])
                if os.path.isdir(text):
                    return text
                if os.path.isfile(text):
                    return os.path.dirname(text)
        if (classname == "WorkerW"):
            #Desktop
            return
        if True or (classname == "CabinetWClass") or (classname == "ExploreWClass"):
            #explorer (or other windows ?) if path in ToolbarWindow32
            self.global_array.clear()
            win32gui.EnumChildWindows(hwnd, self._callback_enumChildWindows, "ToolbarWindow32")
            for i in self.global_array :
                for text in win32gui.GetWindowText(i).split():
                    if os.path.isdir(text):
                        return text
                    if os.path.isfile(text):
                        return os.path.dirname(text)
            return
        return

    def _callback_EnumHandler(self, hwnd, ctx ):
        if win32gui.IsWindowVisible( hwnd ):
            dwExStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE );
            if ((dwExStyle  & win32con.WS_EX_TOPMOST) == win32con.WS_EX_TOPMOST):
                self.global_array.append(hwnd)
    def GetAllOnTopWindowsName(self):
        self.global_array.clear()
        win32gui.EnumWindows( self._callback_EnumHandler, None )
        return self.global_array

    def GetRealPath(self,app):
        if not app:
            return
        if os.path.exists(app):
            return app
        return shutil.which(app)

def Str2Class(module,feat):
    return getattr(sys.modules[module], feat)

def PopUp(title, msg):
    def callback (hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
        if found_pid == pid:
            # if win32gui.GetWindowText(hwnd) == "QTrayIconMessageWindow":
            if "TrayIconMessageWindowClass" in win32gui.GetClassName(hwnd):
                hwnds.append (hwnd)
        return True
    hwnds = []
    pid=win32process.GetCurrentProcessId()
    win32gui.EnumWindows (callback, hwnds)
    if not hwnds:
        return
    hwnd = hwnds[0]
    win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                                (hwnd, 0, win32gui.NIF_INFO, win32con.WM_USER + 20,
                                  None, "Balloon Tooltip", msg, 200, title, win32gui.NIIF_NOSOUND))
    #(hwnd, id, win32gui.NIF_*, CallbackMessage, hicon, Tooltip text (opt), Balloon tooltip text (opt), Timeout (ms), title (opt),  win32gui.NIIF_*)
    return

class ahk():
    def __init__(self):
        self.ahk_mods = {}
        self.ahk_keys = {}
        for item, value in vars(win32con).items():
            if item.startswith("MOD_"):
                self.ahk_mods[item] = value
                self.ahk_mods[value] = item
            elif item.startswith("VK_"):
                self.ahk_keys[item] = value
                self.ahk_keys[value] = item

    def hhk2ahk(self,hhk):
        ahk = ""
        if (not hhk["mod"]) or (not hhk["key"]):
            return ahk
        if hhk["mod"] & self.ahk_mods["MOD_CONTROL"]:
            ahk += "Ctrl + "
        if hhk["mod"] & self.ahk_mods["MOD_WIN"]:
            ahk += "Win + "
        if hhk["mod"] & self.ahk_mods["MOD_SHIFT"]:
            ahk += "Shift + "
        if hhk["mod"] & self.ahk_mods["MOD_ALT"]:
            ahk += "Alt + "
        if hhk["key"] in self.ahk_keys:
            #remove "VK_"
            ahk += self.ahk_keys[hhk["key"]][3:]
        else:
            #TODO: find how to import MAPVK_VK_TO_CHAR
            MAPVK_VK_TO_CHAR=2
            ahk += chr(win32api.MapVirtualKey(hhk["key"],MAPVK_VK_TO_CHAR)).lower()
        return ahk

    def ahk2hhk(self,ahk):
        hhk = {}
        nb_k=0
        nb_m=0
        hhk["mod"] = 0
        arr = ahk.upper()
        arr = arr.split("+")
        if len(arr)<2:
            return {"mod":0}, ahk, "Shortcut too short"+ahk+")"
        for i in range(len(arr)):
            mod = arr[i].strip()
            if mod in ['CTRL',"LCTRL","RCTRL","CONTROL","LCONTROL","RCONTROL"]:
                nb_m += 1
                hhk["mod"] |= self.ahk_mods["MOD_CONTROL"]
            elif mod in ['WIN','LWIN','RWIN','WINDOWS','LWINDOWS','RWINDOWS']:
                nb_m += 1
                hhk["mod"] |= self.ahk_mods["MOD_WIN"]
            elif mod in ['ALT','LALT','RALT']:
                nb_m += 1
                hhk["mod"] |= self.ahk_mods["MOD_ALT"]
            elif mod in ['SHIFT','LSHIFT','RSHIFT','MAJ','LMAJ','RMAJ']:
                hhk["mod"] |= self.ahk_mods["MOD_SHIFT"]
            elif "VK_"+mod in self.ahk_keys:
                hhk["key"] = self.ahk_keys["VK_"+mod]
                nb_k += 1
            elif len(mod)==1:
                k=win32api.VkKeyScan(mod[0].lower())
                k = k & 0xFF
                hhk["key"] = k
                nb_k += 1
            else :
                return {"mod":0}, ahk, "Shortcut not well defined ("+mod+" in "+ahk+")"
        if not 'key' in hhk:
            return {"mod":0}, ahk, "Shortcut without key ("+ahk+")"
        if mod == 0 :
            return {"mod":0}, ahk, "Shortcut without modifier ("+ahk+")"
        if nb_m == 0 :
            return {"mod":0}, ahk, "Shortcut with only Shift modifier ("+ahk+")"
        if nb_k > 1:
            return {"mod":0}, ahk, "Shortcut with several keys ("+ahk+")"
        ahk = self.hhk2ahk(hhk)
        return hhk, ahk, ""

#no import threading in main with:
Lock = threading.Lock
class KThread(threading.Thread):
    """ CREDIT: https://blog.finxter.com/how-to-kill-a-thread-in-python/
        Method 3
        A subclass of threading.Thread, with a kill()method."""
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self._return = ""
        self.killed = False
    def run(self):
        sys.settrace(self.globaltrace)
        try:
            if self._target is not None:
                self._return = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs
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
    def getout(self):
        return self._return
