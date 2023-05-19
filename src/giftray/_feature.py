from . import _icon
from . import _general
import copy

class general:
    def __init__(self,giftray,show):
        self.giftray= giftray
        self.show   = show
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
            k = i.casefold()
            if k == "theme".casefold():
                col = _general.GetOpt(general_conf[i],_general.type.STRING)
                if col != self.giftray.conf_theme:
                    self.conf["theme"] = col
                    self.subconf["theme"] = col
            elif k == "dark".casefold():
                dark = _general.GetOpt(general_conf[i],_general.type.STRING)
                if dark != self.giftray.conf_theme:
                    self.conf["dark"] = dark
                    self.subconf["dark"] = dark
            elif k == "light".casefold():
                light = _general.GetOpt(general_conf[i],_general.type.STRING)
                if light != self.giftray.conf_theme:
                    self.conf["light"] = light
                    self.subconf["light"] = light
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

        others_general = dict()
        if self.module in self.giftray.avail_modules:
            self.error = self.giftray.avail_modules[self.module].GetError()
            general_conf = self.giftray.avail_modules[self.module].GetConf()
            for i in general_conf:
                k = i.casefold()
                if k == "theme".casefold():
                    self.theme = _general.GetOpt(general_conf[i],_general.type.STRING)
                elif k == "dark".casefold():
                    self.dark = _general.GetOpt(val[i],_general.type.STRING)
                elif k == "light".casefold():
                    self.light = _general.GetOpt(val[i],_general.type.STRING)
                else:
                    others_general[i]=general_conf[i]
        others = dict()
        for i in val:
            k = i.casefold()
            if k == "function".casefold():
                pass
            elif k == "ico".casefold():
                self.ico = _general.GetOpt(val[i],_general.type.STRING)
            elif k == "click".casefold():
                self.menu = _general.GetOpt(val[i],_general.type.BOOL)
            elif k == "ahk".casefold():
                self.ahk = _general.GetOpt(val[i],_general.type.STRING)
            elif k == "theme".casefold():
                self.theme = _general.GetOpt(val[i],_general.type.STRING)
            elif k == "dark".casefold():
                self.dark = _general.GetOpt(val[i],_general.type.STRING)
            elif k == "light".casefold():
                self.light = _general.GetOpt(val[i],_general.type.STRING)
            else:
                others[i]=val[i]

        if not self.theme:
            self.theme = 'custom'
        if self.dark or self.light:
            themename = self.theme+'/'+''.join(random.choices(string.digits, k=10))
            self.giftray.colors.copy(self.theme, themename)
            self.theme = themename
            self.giftray.colors.set(self.theme,self.dark,self.light)
        self.iconid = self.giftray.images.create(self.ico,self.show[0],self.theme)

        if self.ahk:
            self.hhk, self.ahk, err = giftray.ahk_translator.ahk2hhk(self.ahk)
            if len(err):
                self.AddError(err)

        others = self._PreInit(others)
        self._Init(others,others_general)

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
        self.contain = []
        self.allopt += 'contain'
        ret_others = dict()
        for i in others:
            k = i.casefold()
            if k == "contain".casefold():
                self.contain = _general.GetOpt(others[i],_general.type.LISTSTRING)
            else:
                ret_others[k] = others[k]
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
        self.thread = _general.KThread(target=self._Run)
        self.active = False
        self.enabled = False
        self.allopt += ['enabled']
        ret_others = dict()
        for k in others:
            if k == "enabled".casefold():
                self.enabled = _general.GetOpt(others[k],_general.type.BOOL)
                self.setopt.append('enabled')
            else:
                ret_others[k] = others[k]
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