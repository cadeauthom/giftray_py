import os
# import sys
import copy
import subprocess
import win32con
import win32api
import win32process
import ctypes
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui
import psutil
import time

from . import _general

class conffield:
    def __init__(self, value, type=_general.gtype.STRING):
        self.type = type
        self.value = _general.GetOpt(value,type)
    #def _print(self):
    #    print(self.value)

class singleobject:
    def __del__(self):
        return

    def __init__(self,show,val,statics):
        self.statics = statics
        self.show    = show
        #self.ahk     = ""
        self.theme   = ""
        self.dark    = ""
        self.light   = ""
        self.menu    = False
        #self.hhk     = []
        self.key     = ""
        self.error   = []
        #self.module  = '_feature'#type(self).__module__[(len(self.up.name)+2):]
        self.name    = type(self).__name__
        self.ico     = ""
        self.parents = []
        self.configuration = dict()
        #self.configuration["Function"] = conffield(self.module+'.'+self.name)
        self.configuration["Function"] = conffield(self.name)
        self.configuration_type = { "Function": _general.gtype.STRING,
                                    "Theme": _general.gtype.STRING,
                                    "Light": _general.gtype.COLOR,
                                    "Dark": _general.gtype.COLOR,
                                    "Ico": _general.gtype.STRING,
                                    "Click": _general.gtype.BOOL,
                                     "Key": _general.gtype.STRING}
                                    # "AHK": _general.gtype.STRING}

        others = dict()
        for i in val:
            k = i.title()
            if k == "Function".title():
                pass
            elif k == "Ico".title():
                self.ico = _general.GetOpt(val[i],_general.gtype.STRING)
                self.configuration["Ico"] = conffield(val[i])
            elif k == "Click".title():
                self.menu = _general.GetOpt(val[i],_general.gtype.BOOL)
                self.configuration["Click"] = conffield(val[i], type=_general.gtype.BOOL)
            # elif k == "Ahk".title():
                # self.ahk = _general.GetOpt(val[i],_general.gtype.STRING)
                # self.configuration["AHK"] = conffield(val[i])
            elif k == 'Key'.title():
                self.key = _general.GetOpt(val[i],_general.gtype.STRING).upper()
                self.configuration["Key"] = conffield(val[i]) 
            elif k == "Theme".title():
                self.theme = _general.GetOpt(val[i],_general.gtype.STRING)
                self.configuration["Theme"] = conffield(val[i])
            elif k == "Dark".title():
                self.dark = _general.GetOpt(val[i],_general.gtype.STRING)
                self.configuration["Dark"] = conffield(val[i])
            elif k == "Light".title():
                self.light = _general.GetOpt(val[i],_general.gtype.STRING)
                self.configuration["Light"] = conffield(val[i])
            else:
                others[i]=val[i]

        # if not self.theme:
            # self.theme = 'other'
        # if self.dark or self.light:
            # themename = self.theme+'/'+''.join(random.choices(string.digits, k=10))
            # self.up.colors.copy(self.theme, themename)
            # self.theme = themename
            # self.up.colors.set(self.theme,self.dark,self.light)
        # if 'colors' in dir(self.up):
            # self.iconid = self.up.images.create(self.ico,self.show[0],self.theme)

        # if self.key:
            # print(self.key)
        # if self.ahk:
            # self.hhk, self.ahk, err = statics.ahk_translator.ahk2hhk(self.ahk)
            # if len(err):
                # self.AddError(err)

        others = self._PreInit(others)
        #self._Init(others,others_general)
        self._Init(others)

    def _PreInit(self,others):
        return others

    def _Init(self,others):
        for i in others:
            self.AddError("'"+i+"' not defined")
        return

    def AddError(self,error):
        self.statics.logger.error(error + " in '" +self.show+"'")
        self.error.append(self.show+': '+error)   
        return

    def IsInMenu(self):
        return self.menu

    def IsOK(self):
        if self.error:
            return False
        return True

    def Check(self):
        self.AddError("Class should not be used as is")
        return

    def IsService(self):
        return 'enabled' in dir(self)

    def IsChild(self):
        return len(self.parents)>0

    def AddParent(self,p):
        if self.IsService():
           return False 
        if not p in self.parents:
            self.parents.append(p)
        return p in self.parents

    def GetHK(self):
        return self.key
        # return self.ahk, self.hhk

    def GetError(self):
        return copy.copy(self.error)

class menu(singleobject):
    def __del__(self):
        singleobject.__del__(self)

    def _PreInit(self,others):
        del self.configuration["Function"]
        del self.configuration_type["Function"]
        self.configuration_type["Contain"] = _general.gtype.LISTSTRING
        self.contain = []
        ret_others = dict()
        for i in others:
            k = i.title()
            if k == "Contain".title():
                self.contain = _general.GetOpt(others[i],_general.gtype.LISTSTRING)
            else:
                ret_others[k] = others[k]
        self.configuration["Contain"] = conffield(self.contain,_general.gtype.LISTSTRING)
        return ret_others

    def GetContain(self):
        return copy.copy(self.contain)

    def Check(self):
        if len(self.contain) == 0:
            self.AddError("Empty menu")
        for c in self.contain:
            if not c in self.statics.dynamics.install['Actions']:
                self.AddError(c+" subaction not installed")
                continue
            if not self.statics.dynamics.install['Actions'][c].AddParent(self.show):
                self.AddError(c+" action cannot be a subaction")
            if not self.statics.dynamics.install['Actions'][c].IsOK():
                self.AddError(c+" subaction not OK")
                continue
        # if not self.menu:
            # for c in self.contain:
                # if not self.statics.dynamics.install['Actions'][c].IsInMenu():
                    # self.AddError(c+" is not usable in menu")
        return

class action(singleobject):
    def __del__(self):
        singleobject.__del__(self)

    def Check(self):
        if self.IsOK():
            # if not self.hhk and not self.menu and not self.IsChild():
            if not self.key and not self.menu and not self.IsChild():
                self.AddError("Nor in (sub)menu or shortcut")
        return

    def Run(self):
        if self.error:
            out = '\n'.join(self.error)
        else:
            try:
                out = self._Run()
            except Exception as e:
                e_str = str(e)
                self.statics.logger.error("Action '" +self.show+ "' failed: "+e_str)
                out = "Action '" +self.show+ "' failed: "+e_str
        #if out and not silent:
        #    _general.PopUp(self.show, out)
        return out

    def _Run(self):
        return

    def _mount_wsl(self,pathL,driveW,driveL,dist):
        if driveW == "" or driveW == " ":
            return
        wsl_path = _general.WindowsHandler().GetRealPath( "wsl.exe" )
        if not wsl_path:
            self.AddError("'wsl.exe' not found")
            return
        file = '~/.bash_mount_msg.sh'
        cmd = "mount | grep \'" + driveW.replace('\\','/') + "\' >/dev/null"
        cmd +=  " || ( ("
        cmd +=          "grep '" + file + "' ~/.bashrc "
        cmd +=          "|| echo -e '\\nif [ -f " + file + " ]; then\\n\\t. " + file + "\\n\\trm " + file + "\\nfi\\n' >>  ~/.bashrc "
        cmd +=      ")"
        cmd +=      " && echo 'sudo -- sh <<EOF' > " + file
        cmd +=      " && echo 'mkdir -p " + driveL + "' >> " + file
        cmd +=      " && echo 'mount -t drvfs " + driveW.replace('\\','/') + " " + driveL + " -o rw,noatime,uid=1000,gid=1000,case=off' >> " + file
        # or -o metadata
        cmd +=      " && echo 'EOF' >> " + file
        cmd +=      " ) >> /dev/null"
        cmd +=  " && echo 'cd " + pathL.replace(' ','\\ ') + "' >> " + file
        wsl_cmd = [wsl_path, '-d', dist, 'bash', '-c', cmd]
        x = subprocess.Popen( wsl_cmd, shell=True)
        x.wait()
        return

class service(singleobject):
    def __del__(self):
        # import ctypes, win32con
        _general.threadKiller(self.thread)
        singleobject.__del__(self)

    def _PreInit(self,others):
        self.configuration_type["Enabled"] = _general.gtype.BOOL
        self.thread = _general.KThread(target=self._Run)
        self.active = False
        self.enabled = False
        ret_others = dict()
        for i in others:
            k = i.title()
            if k == "Enabled".title():
                self.enabled = _general.GetOpt(others[i],_general.gtype.BOOL)
            else:
                ret_others[i] = others[i]
        self.configuration["Enabled"] = conffield(self.enabled,_general.gtype.BOOL)
        return ret_others

    def Check(self):
        # if not self.hhk and not self.menu:
        if not self.key and not self.menu:
            self.AddError("Nor in menu or shortcut")
        return 

    def Run(self):
        if self.active:
            if self.thread.is_alive():
                _general.threadKiller(self.thread)
                self.thread = _general.KThread(target=self._Run)
                out = 'stopped'
            else:
                out = 'already stopped'
            self.active = False
        else:
            if self.thread.is_alive():
                _general.threadKiller(self.thread)
                self.thread = _general.KThread(target=self._Run)
                out = 'restarted'
            else:
                out = 'started'
            self.thread.start()
            self.active = True
            timeout = time.time() + 2
            while not self.thread.is_alive():
                if time.time() > timeout:
                    break
        return out

    def _Run(self):
        return

class script(action):
    def _Init(self,others):
        self.configuration_type["Command"]=_general.gtype.PATH
        self.configuration_type["Arguments"]=_general.gtype.STRING
        self.configuration_type["AsAdmin"]=_general.gtype.BOOL
        self.configuration_type["WSLDist"]=_general.gtype.STRING
        self.cmd = ""
        self.args = ""
        self.admin = False
        self.wslmount = ""

        for i in others:
            k = i.title()
            if k == "Command".title():
                self.cmd = _general.GetOpt(others[i],_general.gtype.STRING)
                self.configuration["Command"] = conffield(self.cmd, type=_general.gtype.STRING)
            elif k == "Arguments".title():
                self.args = _general.GetOpt(others[i],_general.gtype.STRING)
                self.configuration["Arguments"] = conffield(self.args, type=_general.gtype.STRING)
            elif k == "AsAdmin".title():
                self.admin = _general.GetOpt(others[i],_general.gtype.BOOL)
                self.configuration["AsAdmin"] = conffield(self.admin, type=_general.gtype.BOOL)
            elif k == "WSLDist".title():
                self.wsldist = _general.GetOpt(others[i],_general.gtype.STRING)
                self.configuration["WSLMount"] = conffield(self.wslmount, type=_general.gtype.STRING)
            else:
                self.AddError("'"+i+"' not defined")
        self.cmd = os.path.expandvars(self.cmd)
        self.args = os.path.expandvars(self.args)
        if not self.cmd and self.show != 'template':
            self.AddError("cmd not set in '" +self.show+"'")
        else:
            cmd = _general.WindowsHandler().GetRealPath(self.cmd)
            if not cmd:
                self.AddError(self.cmd + " not found in '" +self.show+"'")
            else:
                self.cmd = cmd
        return

    def _Run(self):
        out = self.cmd
        cmd = ' & { Start-Process -WindowStyle hidden "'+self.cmd+'"'
        import shlex
        cmd2=shlex.split(self.args)
        folder=' '
        if self.args:
            args = self.args
            if '$folder' in args or '$folderWSL' in args or self.wsldist:
                folder = _general.WindowsHandler().GetCurrentPath()
                if not folder :
                    folder = ' '
                    folderWSL = '~'
                    driveW = ''
                    driveL = ''
                else:
                    folderWSL,driveW,driveL = _general.WindowsHandler().Path_Win2Lin(folder)
                if '$folderWSL' in args:
                    args = args.replace('$folderWSL',"`\""+folderWSL+"`\"")
                if '$folder' in args:
                    args = args.replace('$folder',"\'"+folder+"\'")
                if self.wsldist:
                    self._mount_wsl(folderWSL,driveW,driveL,self.wsldist)
                #cmd2 = list(map(lambda x: x.replace('$folder', '\"'+folder+'\"'), cmd2))    
            cmd += ' -ArgumentList "' + args+'"'
            out += ' ' + self.args
        if self.admin:
            cmd += ' -Verb RunAs'
            out += ' as admin'
            cmd2 += ['-Verb','RunAs']
        cmd += '}'
        prog = subprocess.Popen(['Powershell',  '-Command', cmd])
        return out
        # print(cmd2)
        # cmd3 = [self.cmd]
        # for k in cmd2:
            # if '$folder' in k:
                # k=k.replace('$folder', folder)
            # if ' ' in k:
                # k="'"+k+"'"
            # cmd3+=[k]
            
        # print(cmd3)
        # prog = subprocess.Popen(cmd3)
        # return out

class stayactive(service):
    def _Init(self,others):
        self.configuration_type["Frequency"]=_general.gtype.UINT
        self.frequency = 60
        for i in others:
            k = i.title()
            if k == "frequency".title():
                a = _general.GetOpt(others[k],_general.gtype.UINT)
                if a:
                    self.frequency = a
                self.configuration["Frequency"] = conffield(a, type=_general.gtype.UINT)
            else:
                self.AddError("'"+i+"' not defined")

    def _Run(self):
        # import clicknium
        # a,b = clicknium.mouse.position()
        # while True:
            # for i in range(self.frequency): time.sleep(1)
            # x,y = clicknium.mouse.position()
            # if x==a and y==b:
              # clicknium.mouse.move(a,b)
            # a,b = clicknium.mouse.position()
        def _move(dif):
            import screeninfo
            import pyautogui
            #Press shift
            pyautogui.press("shift")
            #move from 1
            pos = pyautogui.position()
            sc = None
            for s in screeninfo.get_monitors():
                if ( pos.x >= s.x and
                     pos.y >= s.y and
                     pos.x <= s.x + s.width and
                     pos.y <= s.y + s.height):
                    sc = s
                    break
            if not sc:
                return
            pyautogui.move(0,0)
            to=None
            for d in [[dif,dif],[dif,-dif],[-dif,-dif],[-dif,dif],
                      [dif,0  ],[0  ,-dif],[-dif,0   ],[0   ,dif]]:
                x = pos.x+d[0]
                y = pos.y+d[1]
                if ( x >= sc.x and
                     y >= sc.y and
                     x <= sc.x + sc.width and
                     y <= sc.y + sc.height):
                    pyautogui.move( d[0],d[1])
                    pyautogui.move(-d[0],-d[1])
                    return
            return
        while True:
            #self.frequency=10
            for i in range(int(self.frequency / 2)): time.sleep(1)
            if (self.frequency-0.1) < ((win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0):
                #print (self.frequency-0.1,(win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0)
                #_move(1)
                ctypes.windll.user32.mouse_event(0x0001, 0, 0, 0, 0) # MOUSEEVENTF_MOVE, x+0, y+0, dwData if wheel, dwExtraInfo
        return

class alwaysontop(action):
    def __del__(self):
        currentOnTop = _general.WindowsHandler().GetAllOnTopWindowsName()
        if hasattr(self, "top_hwnd"): 
            for hwnd in self.top_hwnd:
                if hwnd in currentOnTop:
                    win32gui.SetWindowPos(hwnd,
                        win32con.HWND_NOTOPMOST,
                        0,0,0,0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        action.__del__(self)

    def _Init(self,others):
        self.configuration_type.pop("Click")
        self.top_hwnd = set()
        self.menu = False
        for i in others:
            k = i.title()
            if False:
                pass
            else:
                self.AddError("'"+i+"' not defined")
        return

    def _Run(self):
        hwnd = win32gui.GetForegroundWindow()
        classname = win32gui.GetClassName(hwnd)
        if (classname == "WorkerW"):
            return "Unable to OnTop Windows Desktop"
        if (classname == "Shell_TrayWnd"):
            return "Unable to OnTop Windows Tray"
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        name = psutil.Process(pid).name()
        currentOnTop = _general.WindowsHandler().GetAllOnTopWindowsName()
        if not hwnd:
            return "Unable to set windows to top"
        if hwnd in self.top_hwnd:
            # we set it TopMost
            self.top_hwnd.remove(hwnd)
            if hwnd in currentOnTop:
                # it is TopMost
                # NoTopMost the window
                win32gui.SetWindowPos(hwnd,
                    win32con.HWND_NOTOPMOST,
                    0,0,0,0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                return('UnTop '+name)
            else:
                return('(Already) UnTop '+name)
        if hwnd in currentOnTop:
            # already TopMost (don't touch)
            win32gui.SetWindowPos(hwnd,
                win32con.HWND_NOTOPMOST,
                0,0,0,0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            return('UnTop of '+name+' (forced)')# managed outside of '+self.show)
        # NoTopMost the window
        win32gui.SetWindowPos(hwnd,
            win32con.HWND_TOPMOST,
            0,0,0,0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        self.top_hwnd.add(hwnd)
        return "Set OnTop to " + name

class wsl(action):
    def _Init(self,others):
        self.configuration_type["Command"]=_general.gtype.STRING
        self.configuration_type["Uniq"]=_general.gtype.BOOL
        self.configuration_type["Output"]=_general.gtype.STRING
        self.configuration_type["Distribution"]=_general.gtype.STRING
        self.cmd            = ""
        self.uniq           = False
        self.out            = ""
        self.distribution   = ""
        tmp = _general.WindowsHandler().GetRealPath( "wsl.exe" )
        if not tmp:
            self.AddError("'wsl.exe' not found")
            return
        self.wsl_path = tmp
        for i in others:
            k = i.title()
            if k == "Command".title():
                self.cmd = _general.GetOpt(others[i],_general.gtype.STRING)
                self.configuration["Command"] = conffield(self.cmd, type=_general.gtype.STRING)
            elif k == "Uniq".title():
                self.uniq = _general.GetOpt(others[i],_general.gtype.BOOL)
                self.configuration["Uniq"] = conffield(self.uniq, type=_general.gtype.BOOL)
            elif k == "Output".title():
                self.out = _general.GetOpt(others[i],_general.gtype.STRING)
                self.configuration["Output"] = conffield(self.out, type=_general.gtype.STRING)
            elif k == "Distribution".title():
                self.distribution = _general.GetOpt(others[i],_general.gtype.STRING)
                self.configuration["Distribution"] = conffield(self.distribution, type=_general.gtype.STRING)
            else:
                self.AddError("'"+i+"' not defined")
        # if "wsl_path" in others_general:
        #     self.wsl_path = others_general["wsl_path"]
        self.out = os.path.expandvars(self.out)
        self.cmd = os.path.expandvars(self.cmd)
        if not self.cmd and self.show != 'template':
            self.AddError("cmd not set in '" +self.show+"'")
        return

    def _Run(self):
        main_cmd = self.cmd
        if '$folder' in self.cmd:
            pathW = _general.WindowsHandler().GetCurrentPath()
            pathL,driveW,driveL = _general.WindowsHandler().Path_Win2Lin(pathW)
            self._mount_wsl(pathL,driveW,driveL,self.distribution)
            # pathL=pathL.replace(" ","\\ ")
            # if driveW != "":
                # file = '~/.bash_mount_msg.sh'
                # cmd = "mount | grep \'" + driveW + "\' >/dev/null"
                # cmd +=  " || ( ("
                # cmd +=          "grep '" + file + "' ~/.bashrc "
                # cmd +=          "|| echo -e '\\nif [ -f " + file + " ]; then\\n\\t. " + file + "\\n\\trm " + file + "\\nfi\\n' >>  ~/.bashrc "
                # cmd +=      ")"
                # cmd +=      " && echo 'sudo -- sh <<EOF' > " + file
                # cmd +=      " && echo 'mkdir -p " + driveL + "' >> " + file
                # cmd +=      " && echo 'mount -t drvfs \"" + driveW + "\\\" " + driveL + " -o rw,noatime,uid=1000,gid=1000,case=off' >> " + file
                # # or -o metadata
                # cmd +=      " && echo 'EOF' >> " + file
                # cmd +=      " && echo 'cd " + pathL + "' >> " + file
                # cmd +=  ") >> /dev/null"
                # wsl_cmd = [self.wsl_path, 'bash', '-c', cmd]
                # x = subprocess.Popen( wsl_cmd, shell=True)
                # x.wait()
            main_cmd = main_cmd.replace('$folderWSL',pathL)
            main_cmd = main_cmd.replace('$folder',"\'"+pathW+"\'")
        if self.uniq:
            main_cmd = 'ps aux | grep "'+main_cmd+'" |grep -v grep >/dev/null|| '+main_cmd
        if self.out:
            main_cmd += ' > ' + self.out
        wsl_cmd = [self.wsl_path]
        if self.distribution:
            wsl_cmd += ['--distribution', self.distribution]
        wsl_cmd += ['bash', '-c', main_cmd]
        exit_code = subprocess.Popen(wsl_cmd, shell=True)
        return 'Run : '+ self.cmd
