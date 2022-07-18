import logging
import icon

class feature:
    def __init__(self,show,val,main):
        others      = dict()
        self.show   = show
        self.icon   = main.conf_ico_default
        self.ahk    = ""
        self.menu   = False
        self.error  = []
        self.hhk    = ""
        for i in val:
            k = i.casefold()
            if k == "function".casefold():
                self.function = val[i]
            elif k == "ico".casefold():
                self.icon = val[i]
            elif k == "ahk".casefold():
                self.ahk = val[i]
            elif k == "show".casefold():
                self.show = val[i]
            elif k == "menu".casefold():
                self.menu = val[i]
            else:
                others[i]=val[i]

        self._custom_init(others)

        self.hicon = icon.GetIcon(main.iconPath, self.icon)
        if self.ahk:
            #self.hhk = self.ahk
            print(self.ahk)
            if not self.hhk:
                self.error.append("Shortcut not well defined ("+self.ahk+")")
            
        if not self.hhk and not self.menu:
            self.error.append("Nor in menu or shortcut")

        print (self.print_error())

        return

    def _custom_init(self,others):
        for i in others:
            logging.error("'"+i+"' not defined in '" +self.show+"'")
            self.error.append("'"+i+"' not defined")
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

    def print(self):
        return self.show

    def return_conf(self):
        return

    def _custom_return_conf(self):
        return