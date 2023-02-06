from . import _icon
from . import _general

'''
def __init__(self,show,val,giftray):
    obviously called
def _custom_init(self,others):
    by __init__
def get_opt(self):
def _custom_get_opt(self):
    by giftray _print_conf
def run(self):
def _custom_run(self):
    by giftray when click/ahk
def print_error(self, sep='\n', prefix='\t- '):
    by giftray _read_conf
def is_ok(self):
    by giftray _read_conf
#def is_defined(self):
def is_in_menu(self):
    by giftray _read_conf
def get_hk(self):
    by giftray _read_conf
def print(self):
    by giftray _read_conf
'''
class main:
    def __init__(self,show,val,giftray):
        others       = dict()
        self.giftray = giftray
        self.show    = show
        self.module  = type(self).__module__
        self.name    = type(self).__name__
        self.ico     = self.module[(len(self.giftray.name)+2):]+"_"+self.name+".ico"
        self.used_ico= ""
        self.ahk     = ""
        self.menu    = False
        self.error   = []
        self.hhk     = []
        self.color   = ""
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

        self._Init(others)
        iconPath = ""
        if (self.color and self.color!=self.giftray.coloricons):
            iconPath = _icon.ValidateIconPath( path    = self.giftray.iconPath,\
                                              color   = self.color, \
                                              project = self.giftray.name)
        if not iconPath:
            iconPath = self.giftray.iconPath
        self.sicon, self.hicon, self.used_ico = _icon.GetIcon(iconPath, giftray, self.ico)
        if self.ahk:
            self.hhk, self.ahk, err = giftray.ahk_translator.ahk2hhk(self.ahk)
            if len(err):
                self.AddError(err)

        if not self.hhk and not self.menu:
            self.AddError("Nor in menu or shortcut")

        return

    def _Init(self,others):
        for i in others:
            self.AddError("'"+i+"' not defined")
        return

    def GetOpt(self):
        return self._GetOpt()

    def _custom_get_opt(self):
        return []

    def AddError(self,error):
        self.giftray.logger.error(error + " in '" +self.show+"'")
        self.error.append(error)

    def Run(self):
        if self.error:
            out = self.error
        else:
            try:
                out = self._Run()
            except Exception as e:
                e_str = str(e)
                print("Action '" +self.show+ "' failed: "+e_str)
                self.giftray.logger.error("Action '" +self.show+ "' failed: "+e_str)
                out = "Action '" +self.show+ "' failed: "+e_str
        #return out
        if out:
            _general.PopUp(self.giftray.main_hicon, self.show, out)
        return

    def _Run(self):
        return

    def GetError(self):
        return self.error

    def IsOK(self):
        if self.error:
            return False
        return True

    def IsInMenu(self):
        return self.menu

    def GetHK(self):
        return self.ahk, self.hhk
