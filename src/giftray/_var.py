import os
import sys
import posixpath
import shutil
import trace, threading
import win32con
import win32api
import win32process
try:
    import win32gui
except ImportError:
    import winxpgui as win32gui
import psutil
import enum
import re
import json
import logging
import importlib
import inspect
import PyQt6.QtWidgets, PyQt6.QtGui, PyQt6.QtSvg

from . import _general
from . import _feature


class mainvar():
    def __init__(self):
        self.showname       = 'GifTray'
        self.name           = self.showname.casefold()
        self.python         = ( "\\python" in sys.executable )
        self.lockfile       = None
        # self.modules        = ['wsl'.casefold(),'windows'.casefold()]
        # self.modules        = ['feature'.casefold()]
        self.modules        = []
        self.avail_modules  = dict()
        self.template       = dict()
        if self.python:
            self.tempdir = './'
            self.conf    = posixpath.join('./conf' , self.name + '.json')
        else:
            for k in ['TMP','TEMP','USERPROFILE']:
                self.tempdir = os.getenv(k)
                if self.tempdir:
                    break
            if not self.tempdir:
                sys.exit()
            self.conf = posixpath.join(self.tempdir, self.name + '.json')
        if not self._checkLockFile():
            sys.exit()
            return
        filelog = posixpath.join(self.tempdir, self.name+".log")
        logging.basicConfig     ( filename=filelog,
                                  level=0,
                                  encoding='utf-8',
                                  format='%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')
        self.logger = logging.getLogger(__name__)
        '''
        for m in self.modules:
            mod=self.name+'._'+m
            if not mod in sys.modules:
                self.logger.error("Module '" +m+ "' not loaded")
                continue
            tmp = importlib.import_module(mod)
            for fct, obj in inspect.getmembers(tmp):
                if not (inspect.isclass(obj) and fct != 'main'):
                    continue
                if (fct == "general" ):
                    self.avail_modules[m] = _general.Str2Class(mod,fct)(self,m)
                    continue
                full = m+"."+fct
                if mod != obj.__module__:
                    self.logger.error("Issue while loading '" +full+ "': mismatch modules name: '"+m+"'!='"+obj.__module__+"'")
                    continue
                if fct != obj.__name__:
                    self.logger.error("Issue while loading '" +full+ "': mismatch feature name: '"+fct+"'!='"+obj.__name__+"'")
                    continue
                if not "_Run" in (dir(obj)):
                    self.logger.error("Feature '" +full+ "' does not have '_custom_run' defined")
                    continue
                self.template[full] = _general.Str2Class(mod,fct)('template',[],self).configuration_type            
            if not m in self.avail_modules:
                self.avail_modules[m] = _feature.general(self,m)
        '''
        self.template['stayactive'] = _feature.stayactive ('template',[],self).configuration_type
        self.template['wsl']        = _feature.wsl        ('template',[],self).configuration_type
        self.template['alwaysontop']= _feature.alwaysontop('template',[],self).configuration_type
        self.template['script']     = _feature.script     ('template',[],self).configuration_type
        self.template['Folder']     = _feature.menu       ('template',[],self).configuration_type
        self.ahk = _general.ahk()

    def _checkLockFile(self):
        lockfile = posixpath.join(self.tempdir,self.name+'.lock')
        already_running = False
        my_pid      = os.getpid()
        my_process  = psutil.Process(my_pid)
        my_name     = my_process.name()
        my_exe 	    = my_process.exe()
        my_username = my_process.username()
        current_process = None
        if os.path.isfile(lockfile):
            current_pid = 0
            with open(lockfile, 'r') as file:
                current_pid = file.read()
            if current_pid:
                try:
                    current_process = psutil.Process(int(current_pid))
                except:
                    current_process = None
        if current_process:
            current_name     = current_process.name()
            current_exe 	 = current_process.exe()
            current_username = current_process.username()
            if (my_name     == current_name     and
                my_exe      == current_exe and
                my_username == current_username):
                return False
        self.lockfile = lockfile
        self.writeLockFile(force=True)
        return True

    def writeLockFile(self, force=False):
        if not os.path.isfile(self.lockfile) or force:
            with open(self.lockfile, 'w') as file:
                file.write(str(os.getpid()))

    def removeLockFile(self):
        if os.path.isfile(self.lockfile):
            os.remove(self.lockfile)

class trayconf:
    def __init__(self,mainvar):
        self.mainvar=mainvar
        #Init Internal
        # self.internal_type = {  "LogLevel": _general.type.STRING,
                                # "Silent": _general.type.STRING,
                                # "Theme": _general.type.STRING,
                                # "Light": _general.type.COLOR,
                                # "Dark": _general.type.COLOR,
                                # "Ico": _general.type.STRING}
        self.internal = dict()
        self.internal['Icons'] = {
                        'Links' : {},
                        'Images': {
                            'GENERIC_Tray'         : { 'Theme': 'Tray',    'SVG': '<?xml version="1.0" encoding="iso-8859-1"?><svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 456.098 456.098" style="enable-background:new 0 0 456.098 456.098;" xml:space="preserve"><path style="fill:#000000;" d="M309.029,0c-41.273,0-66.873,31.347-80.98,58.514C213.943,31.347,188.343,0,147.069,0 c-31.347,0-56.424,26.122-56.424,57.992c0,32.392,25.078,59.037,56.424,59.037V85.682c-13.584,0-25.078-12.539-25.078-27.69 c0-14.629,11.494-26.645,25.078-26.645c47.02,0,65.829,72.62,65.829,73.143l15.151-3.657l15.151,3.657 c0-0.522,18.808-73.143,65.829-73.143c13.584,0,25.078,12.016,25.078,26.645c0,15.151-11.494,27.69-25.078,27.69v31.347 c31.347,0,56.424-26.645,56.424-59.037C365.453,26.122,340.375,0,309.029,0z"/><rect x="243.722" y="101.355" style="fill:#000000;" width="31.347" height="339.069"/><rect x="181.029" y="101.355" style="fill:#000000;" width="31.347" height="339.069"/><path style="fill:#2ca9bc;" d="M430.237,85.682H25.861c-8.882,0-15.673,6.792-15.673,15.673v99.788 c0,8.882,6.792,15.673,15.673,15.673h10.971v223.608c0,8.882,6.792,15.673,15.673,15.673h351.086 c8.882,0,15.673-6.792,15.673-15.673V216.816h10.971c8.882,0,15.673-6.792,15.673-15.673v-99.788 C445.91,92.473,439.118,85.682,430.237,85.682z M41.535,117.029h373.029v68.441H41.535V117.029z M387.918,424.751H68.18V216.816 h319.739V424.751z"/></svg>'},
                            'GENERIC_Errors'       : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="warning-alt" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M10.25,4.19,2.63,18a2,2,0,0,0,1.75,3H19.62a2,2,0,0,0,1.75-3L13.75,4.19A2,2,0,0,0,10.25,4.19Z" style="fill:#2ca9bc; stroke-width: 2;"></path><line id="primary-upstroke" x1="12.05" y1="17" x2="11.95" y2="17" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5;"></line><path id="primary" d="M12,9v4M10.25,4.19,2.63,18a2,2,0,0,0,1.75,3H19.62a2,2,0,0,0,1.75-3L13.75,4.19A2,2,0,0,0,10.25,4.19Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'},
                            'GENERIC_Exit'         : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="sign-out" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M14.56,18.35,13,17.05a1,1,0,0,1-.11-1.41L14.34,14H7V10h7.34L12.93,8.36A1,1,0,0,1,13,7l1.52-1.3A1,1,0,0,1,16,5.76l4.79,5.59a1,1,0,0,1,0,1.3L16,18.24A1,1,0,0,1,14.56,18.35Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M7,20H4a1,1,0,0,1-1-1V5A1,1,0,0,1,4,4H7" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M14.56,18.35,13,17.05a1,1,0,0,1-.11-1.41L14.34,14H7V10h7.34L12.93,8.36A1,1,0,0,1,13,7l1.52-1.3A1,1,0,0,1,16,5.76l4.79,5.59a1,1,0,0,1,0,1.3L16,18.24A1,1,0,0,1,14.56,18.35Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'},
                            'GENERIC_Reload'       : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="exchange-5" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M7,3a4,4,0,1,0,4,4A4,4,0,0,0,7,3ZM17,21a4,4,0,1,0-4-4A4,4,0,0,0,17,21Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M14.57,4.43a8,8,0,0,1,3.09,1.91,8.13,8.13,0,0,1,2,3.3" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><polyline id="primary-2" data-name="primary" points="17.85 8.81 19.66 9.65 20.5 7.84" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></polyline><path id="primary-3" data-name="primary" d="M4.35,14.36a8.13,8.13,0,0,0,2,3.3,8,8,0,0,0,3.09,1.91" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><polyline id="primary-4" data-name="primary" points="6.15 15.19 4.34 14.35 3.5 16.16" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></polyline><path id="primary-5" data-name="primary" d="M7,3a4,4,0,1,0,4,4A4,4,0,0,0,7,3ZM17,21a4,4,0,1,0-4-4A4,4,0,0,0,17,21Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'},
                            'GENERIC_No-Click'     : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="decrease-circle" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><circle id="secondary" cx="12" cy="12" r="9" style="fill:#2ca9bc; stroke-width: 2;"></circle><path id="primary" d="M7.76,12h8.48M12,3a9,9,0,1,0,9,9A9,9,0,0,0,12,3Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'},
                            'GENERIC_Menu'         : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="add-collection" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><rect id="secondary" x="3" y="3" width="14" height="14" rx="1" style="fill:#2ca9bc; stroke-width: 2;"></rect><path id="primary" d="M7,21H20a1,1,0,0,0,1-1V5" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M7,10h6M10,7v6m7,3V4a1,1,0,0,0-1-1H4A1,1,0,0,0,3,4V16a1,1,0,0,0,1,1H16A1,1,0,0,0,17,16Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'},
                            'GENERIC_About'        : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="chat-alert-left" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M3,11c0-4.42,4-8,9-8s9,3.58,9,8-4,8-9,8A9.87,9.87,0,0,1,9,18.52L4,21l1.19-4.77A7.5,7.5,0,0,1,3,11Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M3,11c0-4.42,4-8,9-8s9,3.58,9,8-4,8-9,8A9.87,9.87,0,0,1,9,18.52L4,21l1.19-4.77A7.5,7.5,0,0,1,3,11Zm9-4v3" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><line id="primary-upstroke" x1="12.05" y1="14.5" x2="11.95" y2="14.5" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5;"></line></svg>'},
                            'GENERIC_Generator'    : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="edit-alt-2" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><polygon id="secondary" points="10.47 9.29 14.71 13.53 7.24 21 3 21 3 16.76 10.47 9.29" style="fill:#2ca9bc; stroke-width: 2;"></polygon><path id="primary" d="M20.41,7.83l-2.88,2.88L13.29,6.47l2.88-2.88a1,1,0,0,1,1.42,0l2.82,2.82A1,1,0,0,1,20.41,7.83ZM3,16.76V21H7.24l7.47-7.47L10.47,9.29Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'},
                            'GENERIC_Help'         : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="help" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M10.91,8.16,9.53,3.35A9,9,0,0,0,3.35,9.53l4.81,1.38A4,4,0,0,1,10.91,8.16ZM8.16,13.09,3.35,14.47a9,9,0,0,0,6.18,6.18l1.38-4.81A4,4,0,0,1,8.16,13.09Zm6.31-9.74L13.09,8.16a4,4,0,0,1,2.75,2.75l4.81-1.38A9,9,0,0,0,14.47,3.35Zm1.37,9.74a4,4,0,0,1-2.75,2.75l1.38,4.81a9,9,0,0,0,6.18-6.18Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M20.42,14.41,16.1,13.17m4.32-3.58L16.1,10.83M3.58,9.59,7.9,10.83M3.58,14.41,7.9,13.17m1.69,7.25,1.24-4.32m2.34,0,1.24,4.32m0-16.84L13.17,7.9m-2.34,0L9.59,3.58M12,3a9,9,0,1,0,9,9A9,9,0,0,0,12,3Zm0,5a4,4,0,1,0,4,4A4,4,0,0,0,12,8Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'},
                            'GENERIC_Configuration': { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="settings" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><path id="secondary" d="M20,10h-.59a1,1,0,0,1-.94-.67v0a1,1,0,0,1,.2-1.14l.41-.41a1,1,0,0,0,0-1.42L17.66,4.93a1,1,0,0,0-1.42,0l-.41.41a1,1,0,0,1-1.14.2h0A1,1,0,0,1,14,4.59V4a1,1,0,0,0-1-1H11a1,1,0,0,0-1,1v.59a1,1,0,0,1-.67.94h0a1,1,0,0,1-1.14-.2l-.41-.41a1,1,0,0,0-1.42,0L4.93,6.34a1,1,0,0,0,0,1.42l.41.41a1,1,0,0,1,.2,1.14v0a1,1,0,0,1-.94.67H4a1,1,0,0,0-1,1v2a1,1,0,0,0,1,1h.59a1,1,0,0,1,.94.67v0a1,1,0,0,1-.2,1.14l-.41.41a1,1,0,0,0,0,1.42l1.41,1.41a1,1,0,0,0,1.42,0l.41-.41a1,1,0,0,1,1.14-.2h0a1,1,0,0,1,.67.94V20a1,1,0,0,0,1,1h2a1,1,0,0,0,1-1v-.59a1,1,0,0,1,.67-.94h0a1,1,0,0,1,1.14.2l.41.41a1,1,0,0,0,1.42,0l1.41-1.41a1,1,0,0,0,0-1.42l-.41-.41a1,1,0,0,1-.2-1.14v0a1,1,0,0,1,.94-.67H20a1,1,0,0,0,1-1V11A1,1,0,0,0,20,10Zm-8,5a3,3,0,1,1,3-3A3,3,0,0,1,12,15Z" style="fill:#2ca9bc; stroke-width: 2;"></path><path id="primary" d="M15,12a3,3,0,1,1-3-3A3,3,0,0,1,15,12Zm5-2h-.59a1,1,0,0,1-.94-.67v0a1,1,0,0,1,.2-1.14l.41-.41a1,1,0,0,0,0-1.42L17.66,4.93a1,1,0,0,0-1.42,0l-.41.41a1,1,0,0,1-1.14.2h0A1,1,0,0,1,14,4.59V4a1,1,0,0,0-1-1H11a1,1,0,0,0-1,1v.59a1,1,0,0,1-.67.94h0a1,1,0,0,1-1.14-.2l-.41-.41a1,1,0,0,0-1.42,0L4.93,6.34a1,1,0,0,0,0,1.42l.41.41a1,1,0,0,1,.2,1.14v0a1,1,0,0,1-.94.67H4a1,1,0,0,0-1,1v2a1,1,0,0,0,1,1h.59a1,1,0,0,1,.94.67v0a1,1,0,0,1-.2,1.14l-.41.41a1,1,0,0,0,0,1.42l1.41,1.41a1,1,0,0,0,1.42,0l.41-.41a1,1,0,0,1,1.14-.2h0a1,1,0,0,1,.67.94V20a1,1,0,0,0,1,1h2a1,1,0,0,0,1-1v-.59a1,1,0,0,1,.67-.94h0a1,1,0,0,1,1.14.2l.41.41a1,1,0,0,0,1.42,0l1.41-1.41a1,1,0,0,0,0-1.42l-.41-.41a1,1,0,0,1-.2-1.14v0a1,1,0,0,1,.94-.67H20a1,1,0,0,0,1-1V11A1,1,0,0,0,20,10Z" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>'},
                            'GENERIC_Empty'        : { 'Theme': 'Default', 'SVG': '<?xml version="1.0" encoding="utf-8"?><svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" id="bracket-square" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><rect id="secondary" x="3" y="3" width="18" height="18" rx="1" transform="translate(24) rotate(90)" style="fill:#2ca9bc; stroke-width: 2;"></rect><path id="primary" d="M14,7h2a1,1,0,0,1,1,1v8a1,1,0,0,1-1,1H14" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M10,7H8A1,1,0,0,0,7,8v8a1,1,0,0,0,1,1h2" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><rect id="primary-3" data-name="primary" x="3" y="3" width="18" height="18" rx="1" transform="translate(24) rotate(90)" style="fill: none; stroke:#000000; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></rect></svg>'},
                            #'SP_MessageBoxQuestion': {}
                            }
                        }
        for i in self.internal['Icons']['Images']:
            k = i[len('GENERIC_'):]
            self.internal['Icons']['Links'][k] = i
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
        self.conf['Generals']['Silent'] = True
        self.conf['Generals']['Icons'] = dict()
        self.conf['Generals']['Themes'] = {
                        'Tray'   : {'Theme': 'MonoWhite',
                                    'Dark':  '',
                                    'Light': ''},
                        'Default': {'Theme': 'Native',
                                    'Dark':  '',
                                    'Light': ''},
                        'Custom' : {'Theme': '',
                                    'Dark':  '',
                                    'Light': ''}}
        '''
        for i in self.internal['Icons']:
            k = i
            if i.startswith('GENERIC_'):
                k = i[len('GENERIC_'):]
            self.conf['Generals']['Icons'][k] = {}
        '''

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

    def getTheme(self, theme, native=True):
        cf = theme.casefold()
        for t in self.internal['Themes']:
            if t.casefold() == cf:
                return t
        if native:
            return "Native"
        return None

    def addTheme(self, new, copy, dark, light):
        if not new:
            return
        n = self.getTheme(new, native=False)
        if n:
            return
        copy = self.getTheme(copy)
        self.internal['Themes'][new] = self.internal['Themes'][copy]
        if dark:
            self.internal['Themes'][new]['Dark'] = dark
        if light:
            self.internal['Themes'][new]['Light'] = light

    def isInTray(self, section):
        return (section in self.conf['Folders']) or (section in self.conf['Actions'])

    def setIco(self, name, path):
        if name in self.conf['Generals']['Icons'] and path:
            self.conf['Generals']['Icons'][name] = path

    def setOpt(self, opt, value):
        if opt in self.conf['Generals']:
            self.conf['Generals'][opt] = value

    def print(self):
        self.write('')

    def write(self,path):
        if path:
            if os.path.exists(path):
                shutil.move(path, path + ".bak")
            with open(path,'w') as file:
                json.dump(self.conf, file, indent = 2)
        else:
            print(json.dumps(self.conf, indent = 2))
        # json_object = json.dumps(self.internal, indent = 2)
        # print(json_object)

    def load(self):
        errors = []
        try:
            with open(self.mainvar.conf,'r') as file:
                config = json.load(file)
        except:
            print(self.mainvar.conf)
            return errors
        for k in config['Generals']:
            if k == 'LogLevel':
                LevelNamesMapping=logging.getLevelNamesMapping()
                levelname = config['Generals']['LogLevel']
                if levelname in LevelNamesMapping:
                    self.conf['Generals']['LogLevel'] = levelname
                    # self.logger.setLevel(level=LevelNamesMapping[levelname])
                else:
                    errors.append('LogLevel->'+k+"not supported")
                continue
            elif k ==  'Silent':
                self.conf['Generals']['Silent'] = config['Generals']['Silent']
                continue
            elif k ==  'Icons':
                for i in config['Generals']['Icons']:
                    # if i in self.conf['Generals']['Icons']:
                        # self.conf['Generals']['Icons'][i] = config['Generals']['Icons'][i]
                    self.conf['Generals']['Icons'][i] = config['Generals']['Icons'][i]
                continue
            elif k == 'Themes':
                for t in config['Generals']['Themes']:
                    for f in config['Generals']['Themes'][t]:
                        self.updateTheme(t, f, config['Generals']['Themes'][t][f])
                continue
            else:
                continue
            '''
            if not isinstance(config['Generals'][k],dict):
                continue
            continue_loop = False
            for i in config['Generals'][k]:
                if isinstance(config['Generals'][k][i], (list, dict, tuple)):
                    continue_loop = True
                    continue
            if continue_loop:
                continue
            self.conf['Generals'][k] = config['Generals'][k]
            '''
        for a in config['Actions']:
            if (not 'Function' in config['Actions'][a]
              or not config['Actions'][a]['Function'] in self.mainvar.template):
                continue
            self.conf['Actions'][a] = dict()
            fct = config['Actions'][a]['Function']
            for k in self.mainvar.template['Folder']:
                if k in config['Actions'][a]:
                    if k in ['Function']:
                        continue
                    self.conf['Actions'][a][k] = config['Actions'][a][k]
                else:
                    self.conf['Actions'][a][k] = None
        for f in config['Folders']:
            # self.conf['Folders']['Contain'] = []
            contain = []
            if 'Contain' in config['Folders'][f]:
                for a in config['Folders'][f]['Contain']:
                    if a in self.conf['Actions']:
                        contain.append(a)
                        # self.conf['Folders']['Contain'].append(a)
            if not contain:
                continue
            self.conf['Folders'][f] = dict()
            self.conf['Folders'][f]['Contain'] = contain
            for k in self.mainvar.template['Folder']:
                if k in config['Folders'][f]:
                    if k in ['Contain']:
                        continue
                    # self.conf['Folders'][f][k] = _general.GetOpt(str(config['Folders'][f][k]),self.mainvar.template['Folder'][k])
                    self.conf['Folders'][f][k] = config['Folders'][f][k]
                else:
                    self.conf['Folders'][f][k] = None
        # Build default themes
        if not self.getTheme(self.conf['Generals']['Themes']['Custom']['Theme'], native=False):
            self.updateTheme('Custom', 'Theme', self.conf['Generals']['Themes']['Default']['Theme'])
        for t in ['Tray','Default','Custom']:
            inittheme = self.getTheme(self.conf['Generals']['Themes'][t]['Theme'])
            if self.conf['Generals']['Themes'][t]['Dark']:
                dark = _general.GetOpt(
                                self.conf['Generals']['Themes'][t]['Dark'],
                                _general.type.COLOR)
            else:
                dark = None
            if self.conf['Generals']['Themes'][t]['Light']:
                light = _general.GetOpt(
                                self.conf['Generals']['Themes'][t]['Light'],
                                _general.type.COLOR)
            else:
                light = None
            if not self.getTheme(t, native=False):
                self.addTheme(t, inittheme, dark, light)
        # Build other themes and links to SVGs
        for type in ['Actions','Folders']:
            for f in self.conf[type]:
                if not self.conf[type][f]['Theme'] :
                    theme = self.conf['Generals']['Themes']['Custom']['Theme']
                else:
                    theme = self.getTheme(self.conf[type][f]['Theme'])
                inittheme = theme
                if self.conf[type][f]['Dark']:
                    dark = _general.GetOpt(self.conf[type][f]['Dark'],_general.type.COLOR)
                    theme += '/Dark='+dark
                else:
                    dark = None
                if self.conf[type][f]['Light']:
                    light = _general.GetOpt(self.conf[type][f]['Light'],_general.type.COLOR)
                    theme += '/Light='+light
                else:
                    light = None
                if not self.getTheme(theme, native=False):
                    self.addTheme(theme, inittheme, dark, light)
                psvgs=[]
                path_svg = None
                if self.conf[type][f]['Ico']:
                    path_ico = os.path.abspath(self.conf[type][f]['Ico'])
                    if os.path.exists(path_ico) and path_ico.endswith('.svg'):
                        path_svg =  path_ico
                    elif not self.conf[type][f]['Ico'].endswith('.svg'):
                        psvgs.append('icons/'+self.conf[type][f]['Ico']+'.svg')
                    else:
                        psvgs.append('icons/'+self.conf[type][f]['Ico'])
                if not path_svg:
                    letter = f[0].casefold()
                    if letter in 'abcdefghijklmnopqrstuvwxyz1234567890':
                        psvgs.append('letters/'+letter+'.svg')
                    else:
                        psvgs.append('letters/number-circle-fill.svg')
                    arrpath = []
                    if not '\\python' in sys.executable:
                        arrpath.append(os.path.dirname(sys.executable))
                    arrpath.append(os.path.dirname(self.mainvar.conf))
                    arrpath.append(os.getcwd())
                    for psvg in psvgs:
                        if path_svg:
                            break
                        for thispath in arrpath:
                            if path_svg:
                                break
                            for endpath in [['svg'],['src','svg']]:
                                path = thispath
                                for k in endpath:
                                    path = posixpath.join(path,k)
                                path = os.path.abspath(posixpath.join( path, psvg))
                                if os.path.exists(path):
                                    path_svg = path
                                    break
                    svg = None
                    if path_svg:
                        for l in self.internal['Icons']['Images']:
                            if ( 'Path' in self.internal['Icons']['Images'][l] and
                                 path_svg == self.internal['Icons']['Images'][l]['Path']):
                                if theme == self.internal['Icons']['Images'][l]['Theme']:
                                    self.internal['Icons']['Links'][f] = l
                                    svg = None
                                    break
                                svg = self.internal['Icons']['Images'][l]['SVG']
                        if f in self.internal['Icons']['Links']:
                            pass
                        else:
                            try:
                                with open(path_svg, 'r') as file:
                                    svg = file.read()
                                if not ( svg.startswith('<?xml') and ('<svg' in svg)):
                                    path_svg = None
                                    svg = None
                            except:
                                path_svg = None
                                svg = None
                    if f in self.internal['Icons']['Links']:
                        pass
                    elif not svg:
                        if theme == self.internal['Icons']['Images']['GENERIC_Empty']['Theme']:
                            self.internal['Icons']['Links'][f] = 'GENERIC_Empty'
                        else:
                            for l in self.internal['Icons']['Images']:
                                if ( l.startswith('GENERIC_Empty_') and
                                     theme == self.internal['Icons']['Images'][l]['Theme']):
                                    print('To Remove Debug is seen')
                                    self.internal['Icons']['Links'][f] = l
                        if not f in self.internal['Icons']['Links']:
                            gen_f = 'GENERIC_Empty_'+f
                            self.internal['Icons']['Links'][f] = gen_f
                            self.internal['Icons']['Images'][gen_f] = {
                                        'Theme' : theme,
                                        'SVG'   : self.internal['Icons']['Images']['GENERIC_Empty']['SVG']
                                        }
                    else:
                        self.internal['Icons']['Links'][f] = f
                        self.internal['Icons']['Images'][f] = {
                                    'Theme' : theme,
                                    'SVG'   : svg,
                                    'Path'  : path_svg
                                    }
        # print(json.dumps(self.internal['Icons'], indent = 2))
        for image in self.internal['Icons']['Images']:
            try:
                img_str = self.internal['Icons']['Images'][image]['SVG']
                d1 = self.internal['Themes'][self.internal['Icons']['Images'][image]['Theme']]['Dark']
                dn = self.internal['Themes']['Native']['Dark']
                l1 = self.internal['Themes'][self.internal['Icons']['Images'][image]['Theme']]['Light']
                ln = self.internal['Themes']['Native']['Light']
                if  l1 != ln:
                    img_str=img_str.replace('#'+dn,'#CompletelyFakeStringToReplaceDark')
                    img_str=img_str.replace('#'+ln,'#'+l1)
                    img_str=img_str.replace('#CompletelyFakeStringToReplaceDark','#'+d1)
                elif d1 != dn:
                    img_str=img_str.replace('#'+dn,'#'+d1)
                self.internal['Icons']['Images'][image]['BuilderSVG'] = PyQt6.QtSvg.QSvgRenderer(PyQt6.QtCore.QByteArray(img_str.encode()))
                self.internal['Icons']['Images'][image]['BuilderImage']= PyQt6.QtGui.QImage(256,256, PyQt6.QtGui.QImage.Format.Format_ARGB32)
                self.internal['Icons']['Images'][image]['BuilderSVG'].render(PyQt6.QtGui.QPainter(self.internal['Icons']['Images'][image]['BuilderImage']))
                self.internal['Icons']['Images'][image]['Icon'] = PyQt6.QtGui.QIcon(PyQt6.QtGui.QPixmap.fromImage(self.internal['Icons']['Images'][image]['BuilderImage']))
            except:
                self.mainvar.logger.error("Image '" +image+ "' without svg or no defined")
                self.internal['Icons']['Images'][image]['Icon'] = PyQt6.QtWidgets.QWidget().style().standardIcon(
                                #PyQt6.QtWidgets.QStyle.StandardPixmap.SP_TitleBarContextHelpButton) #too dark
                                PyQt6.QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion) #too dark

