import logging
import icon
import pynput

class main:
    def __init__(self,show,val,giftray):
        others      = dict()
        self.giftray=giftray
        self.show   = show
        self.icon   = giftray.conf_ico_default
        self.ahk    = ""
        self.menu   = False
        self.error  = []
        self.hhk    = []
        for i in val:
            k = i.casefold()
            if k == "function".casefold():
                #self.function = val[i]
                pass
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

        self.hicon = icon.GetIcon(giftray.iconPath, self.icon)
        if self.ahk:
            self._build_hk()
            if not self.hhk:
                self.error.append("Shortcut not well defined ("+self.ahk+")")
            
        if not self.hhk and not self.menu:
            self.error.append("Nor in menu or shortcut")

        return

    def _custom_init(self,others):
        for i in others:
            logging.error("'"+i+"' not defined in '" +self.show+"'")
            self.error.append("'"+i+"' not defined")
        return

    def action(self):
        try:
            out = self._custom_action()
        except Exception as e:
            e_str = str(e)
            print("Action '" +self.show+ "' failed: "+e_str)
            logging.error("Action '" +self.show+ "' failed: "+e_str)
            out = "Action '" +self.show+ "' failed: "+e_str
        return out

    def _custom_action(self):
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

    def print(self):
        return self.show

    def return_conf(self):
        return

    def _custom_return_conf(self):
        return

    def _build_hk(self):
        if not self.ahk:
            return
        hhk = []
        #create hhk
        if not hhk:
            logging.error("Issue on conversion of ahk ("+self.ahk+")")
            #return
        self.hhk = hhk
        #reconvert
        ahk = ""
        if not ahk:
            logging.error("Issue on revert conversion to ahk ("+self.ahk+")")
        else:
            logging.info("Revert ahk "+ahk+" -> "+self.ahk)
            self.ahk = ahk
        return