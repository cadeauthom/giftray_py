import icon

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
        self.ico     = self.module+"_"+self.name+".ico"
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

        self._custom_init(others)
        iconPath = ""
        if (self.color and self.color!=self.giftray.coloricons):
            iconPath = icon.ValidateIconPath( path    = self.giftray.iconPath,\
                                              color   = self.color, \
                                              project = self.giftray.name)
        if not iconPath:
            iconPath = self.giftray.iconPath
        self.hicon, self.used_ico = icon.GetIcon(iconPath, self.ico)
        if self.ahk:
            self.hhk, self.ahk, err = self.giftray.ahk2hhk(self.ahk)
            if len(err):
                self.error.append(err)
            
        if not self.hhk and not self.menu:
            self.error.append("Nor in menu or shortcut")

        return

    def _custom_init(self,others):
        for i in others:
            self.giftray.logger.error("'"+i+"' not defined in '" +self.show+"'")
            self.error.append("'"+i+"' not defined")
        return

    def get_opt(self):
        return self._custom_get_opt()

    def _custom_get_opt(self):
        return []

    def run(self):
        try:
            out = self._custom_run()
        except Exception as e:
            e_str = str(e)
            print("Action '" +self.show+ "' failed: "+e_str)
            self.giftray.logger.error("Action '" +self.show+ "' failed: "+e_str)
            out = "Action '" +self.show+ "' failed: "+e_str
        return out

    def _custom_run(self):
        return

    def print_error(self, sep='\n', prefix='\t- '):
        return prefix+(sep+prefix).join(self.error)

    def is_ok(self):
        if self.error:
            return False
        return True

    def is_defined(self):
        if self.hhk:
            return True
        if self.menu:
            return True
        return False

    def is_in_menu(self):
        return self.menu

    def get_hk(self):
        return self.ahk, self.hhk
