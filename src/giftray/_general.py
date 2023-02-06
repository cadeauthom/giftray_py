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

def RealPath(app):
    if not app:
        return
    if os.path.exists(app):
        return app
    return shutil.which(app)

def str_to_class(module,feat):
    return getattr(sys.modules[module], feat)

def popup(hicon, title, msg):
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
                                  hicon, "Balloon Tooltip", msg, 200, title, win32gui.NIIF_NOSOUND))
    #(hwnd, id, win32gui.NIF_*, CallbackMessage, hicon, Tooltip text (opt), Balloon tooltip text (opt), Timeout (ms), title (opt),  win32gui.NIIF_*)
    return

def daemon_is_runnung():
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
        if hhk["mod"] & self.ahk_mods["MOD_CONTROL"]:
            ahk += "Ctrl + "
        if hhk["mod"] & self.ahk_mods["MOD_WIN"]:
            ahk += "Win + "
        if hhk["mod"] & self.ahk_mods["MOD_SHIFT"]:
            ahk += "Shift + "
        if hhk["mod"] & self.ahk_mods["MOD_ALT"]:
            ahk += "Alt + "
        if hhk["key"] in self.ahk_keys:
            ahk += self.ahk_keys[hhk["key"]][3:]
        else:
            ahk += chr(hhk["key"]).lower()
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
        self.killed = False
    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)
    def __run(self):
        """Hacked run function, which installs thetrace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
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
