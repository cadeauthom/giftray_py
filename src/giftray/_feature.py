from . import _icon
from . import _general
import copy

class conffield:
    def __init__(self, value, type=_general.type.STRING):
        self.type = type
        self.value = _general.GetOpt(value,type)
    def _print(self):
        print(self.value)

class general:
    def __init__(self,giftray,show):
        self.giftray= giftray
        self.show   = show.title()
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
            k = i.title()
            if k == "Theme".title():
                col = _general.GetOpt(general_conf[i],_general.type.STRING)
                if col != self.giftray.conf_theme:
                    self.configuration["Theme"] = conffield(col)
                    self.conf["Theme".title()] = col
                    self.subconf["Theme".title()] = col
            elif k == "Dark".title():
                dark = _general.GetOpt(general_conf[i],_general.type.STRING)
                if dark != self.giftray.conf_theme:
                    self.configuration["Dark"] = conffield(dark)
                    self.conf["Dark".title()] = dark
                    self.subconf["Dark".title()] = dark
            elif k == "Light".title():
                light = _general.GetOpt(general_conf[i],_general.type.STRING)
                if light != self.giftray.conf_theme:
                    self.configuration["light"] = conffield(light)
                    self.conf["Light".title()] = light
                    self.subconf["Light".title()] = light
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
        self.configuration = dict()
        self.configuration_type = { "Theme": _general.type.STRING,
                                    "Light": _general.type.COLOR,
                                    "Dark": _general.type.COLOR}
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
        self.configuration = dict()
        self.configuration["Function"] = conffield(self.module+'.'+self.name)
        self.configuration_type = { "Function": _general.type.STRING,
                                    "Theme": _general.type.STRING,
                                    "Light": _general.type.COLOR,
                                    "Dark": _general.type.COLOR,
                                    "Ico": _general.type.STRING,
                                    "Click": _general.type.BOOL,
                                    "AHK": _general.type.STRING}

        others_general = dict()
        if self.module in self.giftray.avail_modules:
            self.error = self.giftray.avail_modules[self.module].GetError()
            general_conf = self.giftray.avail_modules[self.module].GetConf()
            for i in general_conf:
                k = i.title()
                if k == "Theme".title():
                    self.theme = _general.GetOpt(general_conf[i],_general.type.STRING)
                    self.configuration["Theme"] = conffield(self.theme)
                elif k == "Dark".title():
                    self.dark = _general.GetOpt(val[i],_general.type.STRING)
                    self.configuration["Dark"] = conffield(self.dark)
                elif k == "Light".title():
                    self.light = _general.GetOpt(val[i],_general.type.STRING)
                    self.configuration["Dark"] = conffield(self.light)
                else:
                    others_general[i]=general_conf[i]
        others = dict()
        for i in val:
            k = i.title()
            if k == "Function".title():
                pass
            elif k == "Ico".title():
                self.ico = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["Ico"] = conffield(val[i])
            elif k == "Click".title():
                self.menu = _general.GetOpt(val[i],_general.type.BOOL)
                self.configuration["Click"] = conffield(val[i], type=_general.type.BOOL)
            elif k == "Ahk".title():
                self.ahk = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["AHK"] = conffield(val[i])
            elif k == "Theme".title():
                self.theme = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["Theme"] = conffield(val[i])
            elif k == "Dark".title():
                self.dark = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["Dark"] = conffield(val[i])
            elif k == "Light".title():
                self.light = _general.GetOpt(val[i],_general.type.STRING)
                self.configuration["Light"] = conffield(val[i])
            else:
                others[i]=val[i]

        if not self.theme:
            self.theme = 'other'
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
        del self.configuration["Function"]
        del self.configuration_type["Function"]
        self.configuration_type["Contain"] = _general.type.LISTSTRING
        self.contain = []
        self.allopt += 'contain'
        ret_others = dict()
        for i in others:
            k = i.title()
            if k == "Contain".title():
                self.contain = _general.GetOpt(others[i],_general.type.LISTSTRING)
            else:
                ret_others[k] = others[k]
        self.configuration["Contain"] = conffield(','.join(self.contain),_general.type.LISTSTRING)
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
        self.configuration_type["Enabled"] = _general.type.BOOL
        self.thread = _general.KThread(target=self._Run)
        self.active = False
        self.enabled = False
        self.allopt += ['enabled']
        ret_others = dict()
        for i in others:
            k = i.title()
            if k == "Enabled".title():
                self.enabled = _general.GetOpt(others[i],_general.type.BOOL)
                self.setopt.append('enabled'.title())
            else:
                ret_others[i] = others[i]
        self.configuration["Enabled"] = conffield(self.enabled,_general.type.BOOL)
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