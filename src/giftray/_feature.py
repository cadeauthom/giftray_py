from . import _icon
from . import _general
import copy

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
            elif k == "ico".casefold():
                self.conf["ico"] = val[i]
                self.subconf["ico"] = val[i]
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
        self.error.append(error)
        return

class main:
    def __init__(self,show,val,giftray):
        self.allopt    = []
        self.setopt    = []
        others_general = dict()
        others       = dict()
        self.giftray = giftray
        self.show    = show
        self.module  = type(self).__module__[(len(self.giftray.name)+2):]
        self.name    = type(self).__name__
        self.ico     = self.module+"_"+self.name+".ico"
        self.used_ico= ""
        self.ahk     = ""
        self.menu    = False
        self.error   = self.giftray.avail_modules[self.module].GetError()
        self.hhk     = []
        self.color   = ""
        general_conf = self.giftray.avail_modules[self.module].GetConf()
        for i in general_conf:
            k = i.casefold()
            if k == "color".casefold():
                self.color = general_conf[i]
            elif k == "ico".casefold():
                self.ico   = general_conf[i]
            else:
                others_general[i]=general_conf[i]
        for i in val:
            k = i.casefold()
            if k == "function".casefold():
                #self.function = val[i]
                pass
            elif k == "ico".casefold():
                self.ico = val[i]
            elif k == "ahk".casefold():
                self.ahk = val[i]
            elif k == "color".casefold():
                self.color = val[i]
            #elif k == "show".casefold():
            #    self.show = val[i]
            elif k == "menu".casefold():
                self.menu = (val[i].lower().capitalize() == "True")
            else:
                others[i]=val[i]

        self._Init(others,others_general)
        iconPath = ""
        if (self.color and self.color!=self.giftray.conf_coloricons):
            iconPath = _icon.ValidateIconPath( path    = self.giftray.iconPath,\
                                              color   = self.color, \
                                              project = self.giftray.name)
        if not iconPath:
            iconPath = self.giftray.iconPath
        self.sicon, self.used_ico = _icon.GetIcon(iconPath, giftray, self.ico)
        if self.ahk:
            self.hhk, self.ahk, err = giftray.ahk_translator.ahk2hhk(self.ahk)
            if len(err):
                self.AddError(err)

        if not self.hhk and not self.menu:
            self.AddError("Nor in menu or shortcut")

        return

    def _Init(self,others,others_general):
        for i in others:
            self.AddError("'"+i+"' not defined")
        return

    def GetOpt(self,sub=False):
        if sub:
            return copy.copy(self.setopt)
        return copy.copy(self.allopt)

    def AddError(self,error):
        self.giftray.logger.error(error + " in '" +self.show+"'")
        self.error.append(error)
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

    def GetError(self):
        return copy.copy(self.error)

    def IsOK(self):
        if self.error:
            return False
        return True

    def IsInMenu(self):
        return self.menu

    def GetHK(self):
        return self.ahk, self.hhk
