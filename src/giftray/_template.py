#import os
#import sys
#import subprocess

from . import _feature
from . import _general

class general(_feature.general):
    pass

class template(_feature.action):
    def _Init(self,others,others_general):
        self.allopt.append("localopt")
        self.localopt = "value"
        for i in others:
            k = i.casefold()
            if k == "localopt".casefold():
                self.localopt = _general.GetOpt(others[i],_general.type.STRING)
                self.setopt.append(k)
            else:
                self.AddError("'"+i+"' not defined")
        #initialisation of path and other variable
        self.localvar = [self.localopt]
        #log useful info
        self.giftray.logger.info("template:set localvar to " + ' '.join(self.localvar))
        return

    def _Run(self):
        #run feature
        #without updating variables
        #can be called several times
        return ('String to be printed in windows notification')

