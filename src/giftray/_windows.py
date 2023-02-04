#import os
#import sys
import subprocess

from . import _feature
from . import _general

class script(_feature.main):
    def _custom_init(self,others):
        self.cmd = ""
        self.args = ""
        self.admin = False
        for i in others:
            k = i.casefold()
            if k == "cmd".casefold():
                self.cmd = others[i]  
            elif k == "args".casefold():
                self.args = others[i]  
            elif k == "admin".casefold():
                self.admin = (others[i].lower().capitalize() == "True")   
            else:
                self.giftray.logger.error("'"+i+"' not defined in '" +self.show+"'")
                self.error.append("'"+i+"' not defined")
        if not self.cmd:
            self.giftray.logger.error("cmd not set in '" +self.show+"'")
            self.error.append("cmd not set in '" +self.show+"'")
        else:
            cmd = _general.RealPath(self.cmd)
            if not cmd:
                self.giftray.logger.error(cmd + "not found in '" +self.show+"'")
                self.error.append(cmd + "not found in '" +self.show+"'")
            else:
                self.cmd = cmd
        return

    def _custom_get_opt(self):
        return ["cmd","args","admin"]

    def _custom_run(self):
        out = self.cmd
        cmd = '& { Start-Process "'+self.cmd+'"'
        if self.args:
            cmd += ' -ArgumentList "' + self.args+'"'
            out += ' ' + self.args
        if self.admin:
            cmd += ' -Verb RunAs'
            out += ' as admin'
        cmd += '}'
        prog = subprocess.Popen(['Powershell ', '-Command', cmd])
        return out

