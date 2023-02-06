import os
import sys
import psutil
import time
import subprocess

from . import _feature
from . import _general

wsl_path = _general.RealPath('wsl.exe')

class proxy(_feature.main):
    def _custom_init(self,others):
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
                    self.giftray.logger.error("'port' is not an integer in '" +self.show+"'")
                    self.error.append("'port' not an intger")
                if self.vcxsrv_timeout < 0 :
                    self.giftray.logger.error("'port' is not positive in '" +self.show+"'")
                    self.error.append("'port' not positive")
            else:
                self.giftray.logger.error("'"+i+"' not defined in '" +self.show+"'")
                self.error.append("'"+i+"' not defined")
        if not self.host:
            self.giftray.logger.error("host not set in '" +self.show+"'")
            self.error.append("host not set in '" +self.show+"'")
        if not wsl_path:
            self.giftray.logger.error("WSL seems not installed on the system")
            self.error.append("WSL not found")
        return

    def _custom_get_opt(self):
        return ["host","port"]

    def _custom_run(self):
        cmd = 'ssh -C2qTnNf ' + self.host +' -D ' + str(self.port)
        wsl_cmd = [wsl_path, 'bash', '-c', 'ps aux | grep "'+cmd+'" |grep -v grep || '+cmd]
        exit_code = subprocess.Popen(wsl_cmd, shell=True)
        return 'Start Proxy '+self.host+' on port '+ str(self.port)

#TODO: move terminator to generic gui
class terminator(_feature.main):
    def _custom_init(self,others):
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
                    self.giftray.logger.error("'vcxsrv_timeout' is not an integer in '" +self.show+"'")
                    self.error.append("'vcxsrv_timeout' not an intger")
                if self.vcxsrv_timeout < 0 :
                    self.giftray.logger.error("'vcxsrv_timeout' is not positive in '" +self.show+"'")
                    self.error.append("'vcxsrv_timeout' not positive") 
                elif self.vcxsrv_timeout > 10:
                    self.giftray.logger.error("'vcxsrv_timeout' is to big in '" +self.show+"'")
                    self.error.append("'vcxsrv_timeout' to big")            
            else:
                self.giftray.logger.error("'"+i+"' not defined in '" +self.show+"'")
                self.error.append("'"+i+"' not defined")
        if not self.confvcxsrv:
            self.giftray.logger.error("'vcxsrv' path is not defined in '" +self.show+"'")
            self.error.append("'vcxsrv' path not defined")
        else:
            tmp = _general.RealPath(self.confvcxsrv)
            if not tmp:
                self.giftray.logger.error("'vcxsrv' does not exist in '" +self.show+"' ("+self.confvcxsrv+")")
                self.error.append("'vcxsrv' ("+self.confvcxsrv+") does not exist")
            else:
                self.giftray.logger.info("'vcxsrv' set to "+tmp)
                self.vcxsrv = tmp
        #not putting C:\Windows\System32\ in case windows upgrade changes the path
        #tmp = _general.RealPath("wsl.exe")
        if not wsl_path:
            self.giftray.logger.error("WSL seems not installed on the system")
            self.error.append("WSL not found")
        # else:
            # self.giftray.logger.info("'wsl' set to "+tmp)
            # self.wsl = tmp
        return

    def _custom_get_opt(self):
        return ["vcxsrv","vcxsrv_timeout"]

    def _custom_run(self):
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
        pathW = _general.GetCurrentPath()
        pathL,driveW,driveL = _Path_Win2Lin(pathW)
        if driveW != "":
            file = '~/.bash_mount_msg.sh'
            cmd = "mount | grep \'" + driveW + "\'"
            cmd +=  " || ( ("
            cmd +=          "grep '" + file + "' ~/.bashrc "
            cmd +=          "|| echo -e '\\nif [ -f " + file + " ]; then\\n\\t. " + file + "\\n\\trm " + file + "\\nfi\\n' >>  ~/.bashrc "
            cmd +=      ")"
            cmd +=      " && echo 'sudo -- sh <<EOF' > " + file
            cmd +=      " && echo 'mkdir -p " + driveL + "' >> " + file
            cmd +=      " && echo 'mount -t drvfs \'" + driveW + "\\\' " + driveL + " -o rw,noatime,uid=1000,gid=1000,case=off' >> " + file
            # or -o metadata
            cmd +=      " && echo 'EOF' >> " + file
            cmd +=      " && echo 'cd " + pathL + "' >> " + file
            cmd +=  ") >> /dev/null"
            wsl_cmd = [wsl_path, 'bash', '-c', cmd]
            x = subprocess.Popen( wsl_cmd, shell=True)
            x.wait()
        wsl_cmd = [wsl_path, 'bash', '-c', 'DISPLAY=localhost' + x_nb + ' terminator --working-directory=' + pathL +'']
        exit_code = subprocess.Popen(wsl_cmd, shell=True)
        return "Start Terminator"
        #OK:exit_code = os.spawnv(os.P_WAIT, _general.RealPath("powershell"),[_general.RealPath("powershell"), "-Command", "\"$host.ui.RawUI.WindowTitle ='" +wsl_cmd[0] + "'; " + ' '.join(wsl_cmd) +"\""])
        #if exit_code == 0:
        #    return "Terminator started"
        #else:
        #    return "Failed to start Terminator"


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
