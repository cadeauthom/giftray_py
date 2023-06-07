import os
import sys
import psutil
import time
import subprocess

from . import _feature
from . import _general

class general(_feature.general):
    def _Init(self):
        self.configuration_type["vcxsrv"]=_general.type.PATH
        self.configuration_type["vcxsrv_timeout"]=_general.type.UINT
        self.show = 'WSL'
        tmp = _general.WindowsHandler().GetRealPath( "wsl.exe" )
        if not tmp:
            self.AddError("'wsl.exe' not found")
        else:
            self.conf["wsl_path"] = tmp
        return

    def _Parse(self,others):
        for i in others:
            k = i.title()
            if k == "vcxsrv".title():
                tmp = _general.GetOpt(others[i],_general.type.PATH)
                if not tmp:
                    self.AddError("'vcxsrv' ("+others[i]+") does not exist")
                else:
                    self.giftray.logger.info("'vcxsrv' set to "+tmp)
                    self.conf["vcxsrv"] = tmp
                    self.subconf["vcxsrv"] = tmp
                    self.configuration["vcxsrv"] = _feature.conffield(tmp, type=_general.type.PATH)
            elif k == "vcxsrv_timeout".title():
                a = _general.GetOpt(others[i],_general.type.UINT)
                if a and a < 10:
                    self.conf["vcxsrv_timeout"] = a
                    self.subconf["vcxsrv_timeout"] = a
                    self.configuration["vcxsrv_timeout"] = _feature.conffield(a, type=_general.type.UINT)
                else:
                    self.AddError("'vcxsrv_timeout' not in [0-10]")
            else:
                self.AddError("'"+i+"' not defined")
        return

class cmd(_feature.action):
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

    def _Init(self,others,others_general):
        self.configuration_type["Command"]=_general.type.STRING
        self.configuration_type["Uniq"]=_general.type.BOOL
        self.configuration_type["GUI"]=_general.type.BOOL
        self.configuration_type["Output"]=_general.type.STRING
        # self.configuration_type["vcxsrv"]=_general.type.PATH
        # self.configuration_type["vcxsrv_timeout"]=_general.type.UINT
        self.allopt         += ["cmd","uniq","gui","out"]
        self.cmd            = ""
        self.uniq           = False
        self.out            = ""
        self.gui            = False
        self.vcxsrv         = ""
        self.vcxsrv_timeout = 2
        confvcxsrv_timeout = 0
        confvcxsrv     = ""
        for i in others:
            k = i.title()
            if k == "cmd".title():
                self.cmd = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
                self.configuration["Command"] = _feature.conffield(self.cmd, type=_general.type.STRING)
            elif k == "gui".title():
                self.gui = _general.GetOpt(others[i],_general.type.BOOL)
                self.setopt.append(k)
                self.configuration["GUI"] = _feature.conffield(self.gui, type=_general.type.BOOL)
            elif k == "uniq".title():
                self.uniq = _general.GetOpt(others[i],_general.type.BOOL)
                self.setopt.append(k)
                self.configuration["Uniq"] = _feature.conffield(self.uniq, type=_general.type.BOOL)
            elif k == "out".title():
                self.out = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
                self.configuration["Output"] = _feature.conffield(self.out, type=_general.type.STRING)
            elif k == "vcxsrv".title():
                tmp = _general.GetOpt(others[i],_general.type.PATH)
                if not tmp:
                    self.AddError("'vcxsrv' ("+others[i]+") does not exist")
                else:
                    self.giftray.logger.info("'vcxsrv' set to "+tmp)
                    self.vcxsrv = tmp
                    self.setopt.append(k.casefold())
                    self.allopt.append(k.casefold())
                    self.configuration["vcxsrv"] = _feature.conffield(tmp, type=_general.type.PATH)
            elif k == "vcxsrv_timeout".title():
                a = _general.GetOpt(others[i],_general.type.UINT)
                if a and a < 10:
                    confvcxsrv_timeout = a
                    self.setopt.append(k.casefold())
                    self.allopt.append(k.casefold())
                    self.configuration["vcxsrv_timeout"] = _feature.conffield(confvcxsrv_timeout, type=_general.type.UINT)
                else:
                    self.AddError("'vcxsrv_timeout' not in [0-10]")
            else:
                self.AddError("'"+i+"' not defined")
        if confvcxsrv_timeout:
            self.vcxsrv_timeout = confvcxsrv_timeout
        elif "vcxsrv_timeout" in others_general:
            self.vcxsrv_timeout = others_general["vcxsrv_timeout"]
        if not self.vcxsrv and "vcxsrv" in others_general:
            self.vcxsrv = others_general["vcxsrv"]
        else:
            self.AddError("'vcxsrv' path not defined")
        if "wsl_path" in others_general:
            self.wsl_path = others_general["wsl_path"]
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
