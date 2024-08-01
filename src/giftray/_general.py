import os
import sys
# import posixpath
import shutil
import threading
# import trace
import win32con
import win32com.client
import win32api
import win32process
import time
import ctypes
try:
    import win32gui
except ImportError:
    import winxpgui as win32gui
# import psutil
import enum
import re
# import json
# import logging
# import importlib
# import inspect

class gtype(enum.Enum):
    UINT        = 1
    INT         = 2
    BOOL        = 3
    STRING      = 4
    LOWSTRING   = 5
    UPSTRING    = 6
    LISTSTRING  = 7
    PATH        = 8
    COLOR       = 9
    # THEME       = 10

# for member in gtype:
    # globals()[member.name] = member

def GetOpt(val,t):
    ret = None
    if t == gtype.UINT:
        try:
            ret = abs(int(val))
        except:
            ret = 0
    elif t == gtype.INT:
        try:
            ret = int(val)
        except:
            ret = 0
    elif t == gtype.BOOL:
        try:
            if val == None:
                ret = True
            else:
                ret = (str(val).title() in ['True'.title(),'On'.title(),'1'.title()])
        except:
            ret = False
    elif t == gtype.STRING:
        try:
            if not val:
                ret = ''
            else:
                ret = str(val)
        except:
            ret = ''
    elif t == gtype.LOWSTRING:
        try:
            if val == None:
                ret = ''
            else:
                ret = str(val).casefold()
        except:
            ret = ''
    elif t == gtype.UPSTRING:
        try:
            if val == None:
                ret = ''
            else:
                ret = str(val).upper()
        except:
            ret = ''
    elif t == gtype.LISTSTRING:
        ret = []
        try:
            for k in val:
                a = GetOpt(k,gtype.STRING)
                if a:
                    ret.append(a)
        except:
            pass
        #
            # ret = re.split('\s*[,;]\s*',val)
            # print(val,'-',ret)
        # except:
            # print(val,'?')
            # ret = []
    elif t == gtype.PATH: #no subpath management, no icon path
        ret = WindowsHandler().GetRealPath(str(val))
    elif t == gtype.COLOR:
        ret = str(val).upper()
        if re.fullmatch(r"^[0-9a-fA-F]{6}$", ret) is None:
            ret = '000000'
    # elif t == gtype.THEME:
        # ret = giftray.colors.GetName(str(t))
    return ret

class WindowsHandler:
    def __init__(self):
        self.global_array = []

    # def _callback_enumChildWindows(self,handle, arg):
        # if win32gui.GetClassName(handle) == arg:
            # self.global_array.append(handle)
        # return True

    def Path_Win2Lin(self,pathW):
        driveL = ""
        driveW = ""
        pathL = "~"
        to_return = ["~","",""] #[linux path, win drive, linux mnt dir]
        if ( pathW == None ) or ( len(pathW) == 0 ):
            #default
            True
        #windows specific directory
        elif pathW.startswith('::'):
            #network drive
            True
        elif pathW.startswith('//'):
            a = pathW[2:].split('/')
            if len(a)<2:
                return to_return
            driveW = "\\\\" + a[0] + "\\" + a[1] #enough \ ?
            a[0]=a[0].lower()
            a[1]=a[1].lower()
            pathL = ("/mnt/" + "/".join(a)).replace(" ","\\ ")
            driveL = "/mnt/" + a[0].replace(" ","_")+ '/' + a[1].replace(" ","_")
        else:
            a = pathW.split(':')
            if len(a)<1 or len(a[0])!=1:
                return to_return
            drive = a[0]
            driveW = drive + ':'
            driveL = "/mnt/" + drive.lower()
            pathL = (driveL + "/".join(a[1].split('\\'))).lower()
        return pathL,driveW,driveL

    def GetCurrentPath(self):
        hwnd      = win32gui.GetForegroundWindow()
        classname = win32gui.GetClassName(hwnd)
        if (classname == "WorkerW"):
            #Desktop
            return ""
        text=win32gui.GetWindowText(hwnd)
        if (classname == "CabinetWClass") or (classname == "ExploreWClass"):
            #explorer (or other windows ?)
            # self.global_array.clear()
            # win32gui.EnumChildWindows(hwnd, self._callback_enumChildWindows, "ToolbarWindow32")
            shell = win32com.client.Dispatch("Shell.Application")
            for window in shell.Windows():
                if window.hwnd != hwnd: continue
                # because in win11 explorer can have tab
                if text==window.LocationName:
                    url=window.LocationURL
                    if url and url.startswith('file'):
                        url=url[5:].replace('///','')
                    else:
                        continue
                    while url and url.endswith('/'):
                        url=url[0:-1]
                    return url+'/'
            return ""
        #other windows: test if windows name contains a path
        #TODO manage wsl path
        full_text = text.split()
        for idx, t in enumerate(full_text):
            if not(len(t)>3 and t[1]==':'):
                continue
            for i in range (len(full_text),idx,-1):
                text = ' '.join(full_text[idx:i])
                # print(text)
                if os.path.isdir(text):
                    return text
                if os.path.isfile(text):
                    return os.path.dirname(text)
        return ""

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

class ahk:
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
        if hhk["mod"] & self.ahk_mods["MOD_WIN"]:
            ahk += "Meta+"
        if hhk["mod"] & self.ahk_mods["MOD_CONTROL"]:
            ahk += "Ctrl+"
        if hhk["mod"] & self.ahk_mods["MOD_SHIFT"]:
            ahk += "Shift+"
        if hhk["mod"] & self.ahk_mods["MOD_ALT"]:
            ahk += "Alt+"
        if hhk["key"] in self.ahk_keys:
            #remove "VK_"
            ahk += self.ahk_keys[hhk["key"]][3:]
        else:
            #TODO: find how to import MAPVK_VK_TO_CHAR
            MAPVK_VK_TO_CHAR=2
            ahk += chr(win32api.MapVirtualKey(hhk["key"],MAPVK_VK_TO_CHAR)).lower()
        return ahk

    def getKey(self,k):
        key=str(k)
        if "VK_"+key in self.ahk_keys:
            return self.ahk_keys["VK_"+key.upper()]
        if len(key)==1:
            k=win32api.VkKeyScan(key.lower())
            k = k & 0xFF
            return k
        if k in self.ahk_keys:
            return self.ahk_keys[k][3:]
        try:
            MAPVK_VK_TO_CHAR=2
            return chr(win32api.MapVirtualKey(k,MAPVK_VK_TO_CHAR)).upper()
        except:
            return None

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
            elif mod in ['WIN','LWIN','RWIN','WINDOWS','LWINDOWS','RWINDOWS','META']:
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

def threadKiller(thread):
    if thread.is_alive():
        thread.kill()
    timeout = time.time() + 1
    while thread.is_alive():
        if time.time() > timeout:
            break
    if thread.is_alive():
        ctypes.windll.user32.PostThreadMessageW(thread.native_id, win32con.WM_QUIT, 0, 0)
    timeout = time.time() + 1
    while thread.is_alive():
        if time.time() > timeout:
            break
    #if thread.is_alive(): .... errors
