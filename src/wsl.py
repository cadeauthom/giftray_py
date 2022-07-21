import os
import sys
import logging
import shutil
import psutil
import time
import subprocess

import feature

#TODO: move terminator to generic gui
class terminator(feature.main):
    def _custom_init(self,others):
        self.confvcxsrv = ""
        self.vcxsrv = ""
        for i in others:
            k = i.casefold()
            if k == "vcxsrv".casefold():
                self.confvcxsrv = others[i]
            else:
                logging.error("'"+i+"' not defined in '" +self.show+"'")
                self.error.append("'"+i+"' not defined")
        if not self.confvcxsrv:
            logging.error("'vcxsrv' path is not defined in '" +self.show+"'")
            self.error.append("'vcxsrv' path not defined")
        else:
            tmp = shutil.which(self.confvcxsrv)
            if not tmp:
                logging.error("'vcxsrv' does not exist in '" +self.show+"' ("+self.confvcxsrv+")")
                self.error.append("'vcxsrv' ("+self.confvcxsrv+") does not exist")
            else:
                logging.info("'vcxsrv' set to "+tmp)
                self.vcxsrv = tmp
        return

    def _custom_action(self):
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
            time.sleep(2)
            if x.poll() != None:
                logging.error("Fail to start vcxsrv in '" +self.show+"' ("+' '.join(x_cmd)+")")
                return "Fail to start vcxsrv : "+' '.join(x_cmd)
        # wmic process get commandline |  Select-String -Pattern vcxsrv
        #f = wmi.WMI()
        #for process in f.Win32_Process():
        #     print(process.commandline)
        return
