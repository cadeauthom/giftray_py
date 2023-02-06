#import os
#import sys
#import subprocess

from . import _feature
from . import _general

class template(_feature.main):
    def _Init(self,others):
        self.localopt = "value"
        for i in others:
            k = i.casefold()
            if k == "localopt".casefold():
                self.confvcxsrv = others[i]
            else:
                self.AddError("'"+i+"' not defined")
        #initialisation of path and other variable
        self.localvar = [self.localopt]
        #log useful info
        self.giftray.logger.info("template:set localvar to " + ' '.join(self.localvar))
        return

    def _GetOpt(self):
        #return options for config
        return ["localopt"]

    def _Run(self):
        #run feature
        #without updating variables
        #can be called several times
        return ('String to be printed in windows notification')

