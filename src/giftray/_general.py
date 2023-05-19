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

class mainmenuconf:
    def __init__(self,colors,images):
        self.colors = colors
        self.images = images
        self.dark   = ''
        self.light  = ''
        self.theme  = 'native'
        self.icos   = dict()
        self.ids    = dict()
    def build(self):
        self.colors.copy('maincustom','default')
        self.colors.copy(self.theme,'default')
        self.colors.set('default',self.dark,self.light)
        for ico in self.images.getDefault():
            path = ''
            id = -1
            pico = ""
            if ico in self.icos:
                pico = self.icos[ico]
            id = self.images.create(pico,'','default',generic=ico)
            path = self.images.getPath(id)
            self.ids[ico] = id
    def getIcon(self,id):
        if 'GENERIC_'+id.title() in self.ids:
            return self.images.getIcon(self.ids['GENERIC_'+id.title()])

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
            if win32gui.GetClassName(hwnd) == "Qt642TrayIconMessageWindowClass":
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

def IsAlreadyRunning():
    ''' TODO
    prebuild fct ? google will help
    or:
    get PID
    if lock file
        read it
        search this PID
        if running: quit
    write lock file
    class __del__ destroy lock
    '''
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
