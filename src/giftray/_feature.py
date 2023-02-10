from . import _icon
from . import _general
import copy
import re

class general:
    def __init__(self,giftray,show):
        self.giftray= giftray
        self.show   = show
        self.Clean()
        self._Init()
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
            k = i.casefold()
            if k == "color".casefold():
                if val[i] != self.giftray.conf_coloricons:
                    self.conf["color"] = val[i]
                    self.subconf["color"] = val[i]
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

class object:
    def __init__(self,show,val,giftray):
        self.allopt  = ["ahk","ico","color"]
        self.setopt  = []
        self.giftray = giftray
        self.show    = show
        self.ahk     = ""
        self.ico     = ""
        self.color   = ""
        self.menu    = False
        self.hhk     = []
        self.error   = []
        self.module  = type(self).__module__[(len(self.giftray.name)+2):]
        self.name    = type(self).__name__
        self.used_ico= ""

        others_general = dict()
        if self.module in self.giftray.avail_modules:
            self.error = self.giftray.avail_modules[self.module].GetError()
            general_conf = self.giftray.avail_modules[self.module].GetConf()
            for i in general_conf:
                k = i.casefold()
                if k == "color".casefold():
                    self.color = general_conf[i]
                else:
                    others_general[i]=general_conf[i]
        others = dict()
        for i in val:
            k = i.casefold()
            if k == "function".casefold():
                pass
            elif k == "ico".casefold():
                self.setopt.append(k)
                if val[i].lower().capitalize() == "True":
                    self.ico = self.module+"_"+self.name+".ico"
                    self.menu=True
                elif val[i].lower().capitalize() == "False":
                    self.menu=False
                else:
                    self.ico = val[i]
                    self.menu=True
            elif k == "ahk".casefold():
                self.setopt.append(k)
                self.ahk = val[i]
            elif k == "color".casefold():
                self.setopt.append(k)
                self.color = val[i]
            else:
                others[i]=val[i]

        iconPath = ""
        if (self.color and self.color!=self.giftray.conf_coloricons):
            iconPath = _icon.ValidateIconPath(path    = self.giftray.iconPath,\
                                              color   = self.color, \
                                              project = self.giftray.name)
        if not iconPath:
            iconPath = self.giftray.iconPath
        self.sicon, self.used_ico = _icon.GetIcon(iconPath, giftray, self.ico)
        if self.ahk:
            self.hhk, self.ahk, err = giftray.ahk_translator.ahk2hhk(self.ahk)
            if len(err):
                self.AddError(err)

        others = self._PreInit(others)
        self._Init(others,others_general)
        self._AddLastInitErrors()

    def _AddLastInitErrors(self):
        self.AddError("Class should not be used as is")
        return

    def _PreInit(self,others):
        return others

    def _Init(self,others,others_general):
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

    def GetHK(self):
        return self.ahk, self.hhk

    def GetError(self):
        return copy.copy(self.error)
        
    def GetOpt(self,sub=False):
        if sub:
            return copy.copy(self.setopt)
        return copy.copy(self.allopt) 

class menu(object):
    def _AddLastInitErrors(self):
        if len(self.contain) == 0:
            self.AddError("No contain set")
        if not self.hhk and not self.menu :
            self.AddError("Nor in menu or shortcut")
        return

    def _PreInit(self,others):
        self.contain = []
        self.allopt += 'contain'
        ret_others = dict()
        for k in others:
            if k == "contain".casefold():
                self.contain = re.split('\s*[,;]\s*',others[k])
            else:
                ret_others[k] = others[k]
        return ret_others

    def GetContain(self):
        return copy.copy(self.contain)

    def CheckContain(self):
        for c in self.contain:
            if not c in self.giftray.install:
                self.AddError(c+" not installed")
                continue
            self.giftray.install[c].AddParent(self.show)
            if not self.giftray.install[c].IsOK():
                self.AddError(c+" not OK")
                continue
        return

class main(object):
    def _PreInit(self,others):
        self.parents = []
        # for p in self.giftray.submenus:
            # if show in giftray.submenus[p].GetContain():
                # self.parents.append(p)
        return others

    def _AddLastInitErrors(self):
        if not self.hhk and not self.menu and not self.IsChild:
            self.AddError("Nor in menu or shortcut")
        return

    def AddParent(self,p):
        if not p in self.parents:
            self.parents.append(p)
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
        #return out
        if out:
            _general.PopUp(self.show, out)
        return

    def _Run(self):
        return

    def IsChild(self):
        return len(self.parents)>0

