import os
import sys
import copy
import subprocess
import win32con
import win32process
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui
import psutil
import time

from . import _icon
from . import _general

class conffield:
    def __init__(self, value, type=_general.type.STRING):
        self.type = type
        self.value = _general.GetOpt(value,type)
    def _print(self):
        print(self.value)

'''
class general:
    def __init__(self,giftray,show):
        self.giftray= giftray
        self.show   = show.title()
        self.Clean()
        return

    def _Init(self):
        return

    def Parse(self,val):
        if self.set :
            self.AddError("General configuration set several times for "+self.show)
            return
        if self.used :
            self.AddError("General configuration set after being used for "+self.show)
            return
        self.set = True
        others = dict()
        for i in val:
            k = i.title()
            if k == "Theme".title():
                col = _general.GetOpt(general_conf[i],_general.type.STRING)
                if col != self.giftray.conf_theme:
                    self.configuration["Theme"] = conffield(col)
                    self.conf["Theme".title()] = col
                    self.subconf["Theme".title()] = col
            elif k == "Dark".title():
                dark = _general.GetOpt(general_conf[i],_general.type.STRING)
                if dark != self.giftray.conf_theme:
                    self.configuration["Dark"] = conffield(dark)
                    self.conf["Dark".title()] = dark
                    self.subconf["Dark".title()] = dark
            elif k == "Light".title():
                light = _general.GetOpt(general_conf[i],_general.type.STRING)
                if light != self.giftray.conf_theme:
                    self.configuration["light"] = conffield(light)
                    self.conf["Light".title()] = light
                    self.subconf["Light".title()] = light
            else:
                others[i]=val[i]
        self._Parse(others)
        return

    def _Parse(self,others):
        for i in others:
            self.AddError("'"+i+"' not defined")
        return

    def Clean(self):
        self.error  = []
        self.conf   = dict()
        self.subconf= dict()
        self.set    = False
        self.used   = False
        self.configuration = dict()
        self.configuration_type = { "Theme": _general.type.STRING,
                                    "Light": _general.type.COLOR,
                                    "Dark": _general.type.COLOR}
        self._Init()
        return

    def GetConf(self,partial=False):
        self.used = True
        if partial: return copy.copy(self.subconf)
        return copy.copy(self.conf)

    def GetError(self):
        return copy.copy(self.error)

    def AddError(self,error):
        self.giftray.logger.error(error + " in '" +self.show+"'")
        self.error.append(self.show+': '+error)
        return
'''

class object:
    def __del__(self):
        return

    def __init__(self,show,val,giftray):
        self.allopt  = []
        self.setopt  = []
        self.giftray = giftray
        self.show    = show
        self.ahk     = ""
        self.theme   = ""
        self.dark    = ""
        self.light   = ""
        self.menu    = False
        self.hhk     = []
        self.error   = []
        self.module  = type(self).__module__[(len(self.giftray.name)+2):]
        self.name    = type(self).__name__
        self.ico     = ""
        self.parents = []
        self.configuration = dict()
        self.configuration["Function"] = conffield(self.module+'.'+self.name)
        self.configuration_type = { "Function": _general.type.STRING,
                                    "Theme": _general.type.STRING,
                                    "Light": _general.type.COLOR,
                                    "Dark": _general.type.COLOR,
                                    "Ico": _general.type.STRING,
                                    "Click": _general.type.BOOL,
                                    "AHK": _general.type.STRING}

        #others_general = dict()
        if self.module in self.giftray.avail_modules:
            self.error = self.giftray.avail_modules[self.module].GetError()
            '''
            general_conf = self.giftray.avail_modules[self.module].GetConf()
            for i in general_conf:
                k = i.title()
                if k == "Theme".title():
                    self.theme = _general.GetOpt(general_conf[i],_general.type.STRING)
                    self.configuration["Theme"] = conffield(self.theme)
                elif k == "Dark".title():
                    self.dark = _general.GetOpt(val[i],_general.type.STRING)
                    self.configuration["Dark"] = conffield(self.dark)
                elif k == "Light".title():
                    self.light = _general.GetOpt(val[i],_general.type.STRING)
                    self.configuration["Dark"] = conffield(self.light)
                else:
                    others_general[i]=general_conf[i]
            '''
        others = dict()
        for i in val:
            k = i.title()
            if k == "Function".title():
                pass
            elif k == "Ico".title():
                self.ico = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["Ico"] = conffield(val[i])
            elif k == "Click".title():
                self.menu = _general.GetOpt(val[i],_general.type.BOOL)
                self.configuration["Click"] = conffield(val[i], type=_general.type.BOOL)
            elif k == "Ahk".title():
                self.ahk = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["AHK"] = conffield(val[i])
            elif k == "Theme".title():
                self.theme = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["Theme"] = conffield(val[i])
            elif k == "Dark".title():
                self.dark = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["Dark"] = conffield(val[i])
            elif k == "Light".title():
                self.light = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["Light"] = conffield(val[i])
            else:
                others[i]=val[i]

        if not self.theme:
            self.theme = 'other'
        if self.dark or self.light:
            themename = self.theme+'/'+''.join(random.choices(string.digits, k=10))
            self.giftray.colors.copy(self.theme, themename)
            self.theme = themename
            self.giftray.colors.set(self.theme,self.dark,self.light)
        if 'colors' in dir(self.giftray):
            self.iconid = self.giftray.images.create(self.ico,self.show[0],self.theme)

        if self.ahk:
            self.hhk, self.ahk, err = giftray.ahk_translator.ahk2hhk(self.ahk)
            if len(err):
                self.AddError(err)

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
        self.giftray.logger.error(error + " in '" +self.show+"'")
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
        return self.ahk, self.hhk

    def GetError(self):
        return copy.copy(self.error)
        
    def GetOpt(self,sub=False):
        if sub:
            return copy.copy(self.setopt)
        return copy.copy(self.allopt)

class menu(object):
    def __del__(self):
        object.__del__(self)

    def _PreInit(self,others):
        del self.configuration["Function"]
        del self.configuration_type["Function"]
        self.configuration_type["Contain"] = _general.type.LISTSTRING
        self.contain = []
        self.allopt += 'contain'
        ret_others = dict()
        for i in others:
            k = i.title()
            if k == "Contain".title():
                self.contain = _general.GetOpt(others[i],_general.type.LISTSTRING)
            else:
                ret_others[k] = others[k]
        self.configuration["Contain"] = conffield(','.join(self.contain),_general.type.LISTSTRING)
        return ret_others

    def GetContain(self):
        return copy.copy(self.contain)

    def Check(self):
        if len(self.contain) == 0:
            self.AddError("Empty menu")
        for c in self.contain:
            if not c in self.giftray.install:
                self.AddError(c+" subaction not installed")
                continue
            if not self.giftray.install[c].AddParent(self.show):
                self.AddError(c+" action cannot be a subaction")
            if not self.giftray.install[c].IsOK():
                self.AddError(c+" subaction not OK")
                continue
        if not self.menu:
            for c in self.contain:
                if not self.giftray.install[c].IsInMenu():
                    self.AddError(c+" is not in usable in menu")
        return

class action(object):
    def __del__(self):
        object.__del__(self)

    def Check(self):
        if self.IsOK():
            if not self.hhk and not self.menu and not self.IsChild():
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
                self.giftray.logger.error("Action '" +self.show+ "' failed: "+e_str)
                out = "Action '" +self.show+ "' failed: "+e_str
        #if out and not silent:
        #    _general.PopUp(self.show, out)
        return out

    def _Run(self):
        return

class service(object):
    def __del__(self):
        import ctypes, win32con
        if self.thread.is_alive():
            self.thread.kill()
        object.__del__(self)

    def _PreInit(self,others):
        self.configuration_type["Enabled"] = _general.type.BOOL
        self.thread = _general.KThread(target=self._Run)
        self.active = False
        self.enabled = False
        self.allopt += ['enabled']
        ret_others = dict()
        for i in others:
            k = i.title()
            if k == "Enabled".title():
                self.enabled = _general.GetOpt(others[i],_general.type.BOOL)
                self.setopt.append('enabled'.title())
            else:
                ret_others[i] = others[i]
        self.configuration["Enabled"] = conffield(self.enabled,_general.type.BOOL)
        return ret_others

    def Check(self):
        if not self.hhk and not self.menu:
            self.AddError("Nor in menu or shortcut")
        return 

    def Run(self):
        if self.active:
            if self.thread.is_alive():
                self.thread.kill()
                self.thread = _general.KThread(target=self._Run)
                out = 'stopped'
            else:
                out = 'already stopped'
            self.active = False
        else:
            if self.thread.is_alive():
                self.thread.kill()
                self.thread = _general.KThread(target=self._Run)
                out = 'restarted'
            else:
                out = 'started'
            self.thread.start()
            self.active = True
        return out

    def _Run(self):
        return

class script(action):
    #ToDo: add Uniq option (for startx)
    def _Init(self,others):
        self.configuration_type["Command"]=_general.type.PATH
        self.configuration_type["Arguments"]=_general.type.STRING
        self.configuration_type["AsAdmin"]=_general.type.BOOL
        self.allopt += ["cmd","args","admin"]
        self.cmd = ""
        self.args = ""
        self.admin = False
        for i in others:
            k = i.title()
            if k == "cmd".title():
                self.cmd = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
                self.configuration["Command"] = conffield(self.cmd, type=_general.type.STRING)
            elif k == "args".title():
                self.args = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
                self.configuration["Arguments"] = conffield(self.args, type=_general.type.STRING)
            elif k == "admin".title():
                self.admin = _general.GetOpt(others[i],_general.type.BOOL)
                self.setopt.append(k)
                self.configuration["AsAdmin"] = conffield(self.admin, type=_general.type.BOOL)
            else:
                self.AddError("'"+i+"' not defined")
        if not self.cmd:
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
        if self.args:
            cmd += ' -ArgumentList "' + self.args+'"'
            out += ' ' + self.args
        if self.admin:
            cmd += ' -Verb RunAs'
            out += ' as admin'
        cmd += '}'
        prog = subprocess.Popen(['Powershell',  '-Command', cmd])
        return out

class stayactive(service):
    def _Init(self,others):
        self.configuration_type["Frequency"]=_general.type.UINT
        self.allopt += ["frequency"]
        self.frequency = 60
        for i in others:
            k = i.title()
            if k == "frequency".title():
                a = _general.GetOpt(others[k],_general.type.UINT)
                if a:
                    self.frequency = a
                self.configuration["Frequency"] = conffield(a, type=_general.type.UINT)
            else:
                self.AddError("'"+i+"' not defined")

    def _Run(self):
        import clicknium
        a,b = clicknium.mouse.position()
        while True:
            for i in range(self.frequency): time.sleep(1)
            x,y = clicknium.mouse.position()
            if x==a and y==b:
              clicknium.mouse.move(a,b)
            a,b = clicknium.mouse.position()
        return

class alwaysontop(action):
    def __del__(self):
        currentOnTop = _general.WindowsHandler().GetAllOnTopWindowsName()
        for hwnd in self.top_hwnd:
            if hwnd in currentOnTop:
                win32gui.SetWindowPos(hwnd,
                    win32con.HWND_NOTOPMOST,
                    0,0,0,0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        action.__del__(self)

    def _Init(self,others):
        self.configuration_type.pop("Click")
        self.allopt += []
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
            return('OnTop of '+name+'managed outside of '+self.show)
        # NoTopMost the window
        win32gui.SetWindowPos(hwnd,
            win32con.HWND_TOPMOST,
            0,0,0,0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        self.top_hwnd.add(hwnd)
        return "Set OnTop to " + name

class wsl(action):
    #ToDo: put startx in a script action
    def _StartX(self):
        x_running   = False
        x_nb        = 0
        all_nb      = []
        vcxsrv = self.vcxsrv
        for proc in psutil.process_iter(['exe','cmdline','status']):
            if vcxsrv != proc.info['exe']:
                continue
            for arg in proc.info['cmdline']:
                if arg.startswith(':'):
                    last_nb = int(arg[1:])
            if proc.info['status'] == 'running':
                x_nb = last_nb
                x_running = True
                break
            all_nb.append(last_nb)
            while x_nb in all_nb :
                x_nb += 1
        x_nb = ":"+str(x_nb)
        if not x_running:
            x_cmd = [vcxsrv, x_nb, "-ac","-terminate","-lesspointer","-multiwindow","-clipboard","-wgl","-dpi","auto"]
            x = subprocess.Popen( x_cmd, shell=True)
            time.sleep(2)# ToDo self.vcxsrv_timeout)
            if x.poll() != None:
                self.giftray.logger.error("Fail to start vcxsrv in '" +self.show+"' ("+' '.join(x_cmd)+")")
                return
        return x_nb

    def _Path_Win2Lin(self,pathW):
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
        elif pathW.startswith('\\\\'):
            a = pathW[2:].split('\\')
            if len(a)<2:
                return to_return
            drive = a[0]
            pathL = ("/mnt/" + "/".join(a)).replace(" ","\\ ").lower()
            driveW = "\\\\" + drive #enough \ ?
            driveL = "/mnt/" + drive.replace(" ","_").lower()
        else:
            a = pathW.split(':')
            if len(a)<1 or len(a[0])!=1:
                return to_return
            drive = a[0]
            driveW = drive + ':'
            driveL = "/mnt/" + drive.lower()
            pathL = (driveL + "/".join(a[1].split('\\'))).replace(" ","\\ ").lower()
        return pathL,driveW,driveL

    def _Init(self,others):
        self.configuration_type["Command"]=_general.type.STRING
        self.configuration_type["Uniq"]=_general.type.BOOL
        self.configuration_type["GUI"]=_general.type.BOOL
        self.configuration_type["Output"]=_general.type.STRING
        self.configuration_type["vcxsrv"]=_general.type.PATH
        self.configuration_type["vcxsrv_timeout"]=_general.type.UINT
        self.allopt         += ["cmd","uniq","gui","out"]
        self.cmd            = ""
        self.uniq           = False
        self.out            = ""
        self.gui            = False
        self.vcxsrv         = ""
        self.vcxsrv_timeout = 2
        confvcxsrv_timeout = 0
        confvcxsrv     = ""
        tmp = _general.WindowsHandler().GetRealPath( "wsl.exe" )
        if not tmp:
            self.AddError("'wsl.exe' not found")
            return
        self.wsl_path = tmp
        for i in others:
            k = i.title()
            if k == "cmd".title():
                self.cmd = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
                self.configuration["Command"] = conffield(self.cmd, type=_general.type.STRING)
            elif k == "gui".title():
                self.gui = _general.GetOpt(others[i],_general.type.BOOL)
                self.setopt.append(k)
                self.configuration["GUI"] = conffield(self.gui, type=_general.type.BOOL)
            elif k == "uniq".title():
                self.uniq = _general.GetOpt(others[i],_general.type.BOOL)
                self.setopt.append(k)
                self.configuration["Uniq"] = conffield(self.uniq, type=_general.type.BOOL)
            elif k == "out".title():
                self.out = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
                self.configuration["Output"] = conffield(self.out, type=_general.type.STRING)
            elif k == "vcxsrv".title():
                tmp = _general.GetOpt(others[i],_general.type.PATH)
                if not tmp:
                    self.AddError("'vcxsrv' ("+others[i]+") does not exist")
                else:
                    self.giftray.logger.info("'vcxsrv' set to "+tmp)
                    self.vcxsrv = tmp
                    self.setopt.append(k.casefold())
                    self.allopt.append(k.casefold())
                    self.configuration["vcxsrv"] = conffield(tmp, type=_general.type.PATH)
            elif k == "vcxsrv_timeout".title():
                a = _general.GetOpt(others[i],_general.type.UINT)
                if a and a < 10:
                    confvcxsrv_timeout = a
                    self.setopt.append(k.casefold())
                    self.allopt.append(k.casefold())
                    self.configuration["vcxsrv_timeout"] = conffield(confvcxsrv_timeout, type=_general.type.UINT)
                else:
                    self.AddError("'vcxsrv_timeout' not in [0-10]")
            else:
                self.AddError("'"+i+"' not defined")
        if confvcxsrv_timeout:
            self.vcxsrv_timeout = confvcxsrv_timeout
        # elif "vcxsrv_timeout" in others_general:
        #     self.vcxsrv_timeout = others_general["vcxsrv_timeout"]
        if self.vcxsrv:
            pass
        # elif "vcxsrv" in others_general:
        #     self.vcxsrv = others_general["vcxsrv"]
        else:
            self.AddError("'vcxsrv' path not defined")
        # if "wsl_path" in others_general:
        #     self.wsl_path = others_general["wsl_path"]
        if not self.cmd:
            self.AddError("cmd not set in '" +self.show+"'")
        if self.gui:
            self.uniq = False
        return

    def _Run(self):
        main_cmd = self.cmd
        if '$folder' in self.cmd:
            pathW = _general.WindowsHandler().GetCurrentPath()
            pathL,driveW,driveL = self._Path_Win2Lin(pathW)
            if driveW != "":
                file = '~/.bash_mount_msg.sh'
                cmd = "mount | grep \'" + driveW + "\' >/dev/null"
                cmd +=  " || ( ("
                cmd +=          "grep '" + file + "' ~/.bashrc "
                cmd +=          "|| echo -e '\\nif [ -f " + file + " ]; then\\n\\t. " + file + "\\n\\trm " + file + "\\nfi\\n' >>  ~/.bashrc "
                cmd +=      ")"
                cmd +=      " && echo 'sudo -- sh <<EOF' > " + file
                cmd +=      " && echo 'mkdir -p " + driveL + "' >> " + file
                cmd +=      " && echo 'mount -t drvfs \"" + driveW + "\\\" " + driveL + " -o rw,noatime,uid=1000,gid=1000,case=off' >> " + file
                # or -o metadata
                cmd +=      " && echo 'EOF' >> " + file
                cmd +=      " && echo 'cd " + pathL + "' >> " + file
                cmd +=  ") >> /dev/null"
                wsl_cmd = [self.wsl_path, 'bash', '-c', cmd]
                x = subprocess.Popen( wsl_cmd, shell=True)
                x.wait()
            main_cmd = main_cmd.replace('$folder',pathL)
        if self.uniq:
            main_cmd = 'ps aux | grep "'+main_cmd+'" |grep -v grep >/dev/null|| '+main_cmd
        if self.out:
            main_cmd += ' > ' + self.out
        if self.gui:
            x_nb = self._StartX()
            if not x_nb:
                return "Fail to start vcxsrv"
            main_cmd = 'DISPLAY=localhost' + x_nb + ' ' + main_cmd
        wsl_cmd = [self.wsl_path, 'bash', '-c', main_cmd]
        exit_code = subprocess.Popen(wsl_cmd, shell=True)
        return 'Run : '+ self.cmd
