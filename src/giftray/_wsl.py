import os
import sys
import psutil
import time
import subprocess

from . import _feature
from . import _general

wsl_path = _general.WindowsHandler().GetRealPath('wsl.exe')

class default_wsl(_feature.main):
    def _Path_Win2Lin(pathW):
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

class proxy(default_wsl):
    def _Init(self,others):
        self.host = ""
        self.port = 8080
        for i in others:
            k = i.casefold()
            if k == "host".casefold():
                self.host = others[i]
            elif k == "port".casefold():
                try:
                    self.port = int(others[i])
                except ValueError:
                    self.AddError("'port' not an intger")
                if self.vcxsrv_timeout < 0 :
                    self.AddError("'port' not positive")
            else:
                self.AddError("'"+i+"' not defined")
        if not self.host:
            self.AddError("host not set in '" +self.show+"'")
        if not wsl_path:
            self.AddError("WSL not found")
        return

    def _GetOpt(self):
        return ["host","port"]

    def _Run(self):
        cmd = 'ssh -C2qTnNf ' + self.host +' -D ' + str(self.port)
        wsl_cmd = [wsl_path, 'bash', '-c', 'ps aux | grep "'+cmd+'" |grep -v grep || '+cmd]
        exit_code = subprocess.Popen(wsl_cmd, shell=True)
        return 'Start Proxy '+self.host+' on port '+ str(self.port)

#TODO: move terminator to generic gui
class terminator(default_wsl):
    def _Init(self,others):
        self.confvcxsrv = ""
        self.vcxsrv = ""
        # self.wsl = ""
        self.vcxsrv_timeout = 2
        for i in others:
            k = i.casefold()
            if k == "vcxsrv".casefold():
                self.confvcxsrv = others[i]
            elif k == "vcxsrv_timeout".casefold():
                try:
                    self.vcxsrv_timeout = int(others[i])
                except ValueError:
                    self.AddError("'vcxsrv_timeout' not an intger")
                if self.vcxsrv_timeout < 0 :
                    self.AddError("'vcxsrv_timeout' not positive")
                elif self.vcxsrv_timeout > 10:
                    self.AddError("'vcxsrv_timeout' to big")
            else:
                self.AddError("'"+i+"' not defined")
        if not self.confvcxsrv:
            self.AddError("'vcxsrv' path not defined")
        else:
            tmp = _general.WindowsHandler().GetRealPath(self.confvcxsrv)
            if not tmp:
                self.AddError("'vcxsrv' ("+self.confvcxsrv+") does not exist")
            else:
                self.giftray.logger.info("'vcxsrv' set to "+tmp)
                self.vcxsrv = tmp
        #not putting C:\Windows\System32\ in case windows upgrade changes the path
        #tmp = _general.WindowsHandler().GetRealPath("wsl.exe")
        if not wsl_path:
            self.AddError("WSL not found")
        # else:
            # self.giftray.logger.info("'wsl' set to "+tmp)
            # self.wsl = tmp
        return

    def _GetOpt(self):
        return ["vcxsrv","vcxsrv_timeout"]

    def _Run(self):
        x_running   = False
        x_nb        = 0
        all_nb      = []
        for proc in psutil.process_iter(['exe','cmdline','status']):
            if self.vcxsrv != proc.info['exe']:
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
            x_cmd = [self.vcxsrv, x_nb, "-ac","-terminate","-lesspointer","-multiwindow","-clipboard","-wgl","-dpi","auto"]
            x = subprocess.Popen( x_cmd, shell=True)
            time.sleep(self.vcxsrv_timeout)
            if x.poll() != None:
                self.giftray.logger.error("Fail to start vcxsrv in '" +self.show+"' ("+' '.join(x_cmd)+")")
                return "Fail to start vcxsrv : "+' '.join(x_cmd)
        pathW = _general.WindowsHandler().GetCurrentPath()
        pathL,driveW,driveL = default_wsl._Path_Win2Lin(pathW)
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
            wsl_cmd = [wsl_path, 'bash', '-c', cmd]
            x = subprocess.Popen( wsl_cmd, shell=True)
            x.wait()
        cmd = 'DISPLAY=localhost' + x_nb + ' terminator --working-directory ' + pathL
        wsl_cmd = [wsl_path, 'bash', '-c', cmd]
        exit_code = subprocess.Popen(wsl_cmd, shell=True)
        return "Start Terminator"
