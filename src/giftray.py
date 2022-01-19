



import os
import sys
import win32api         # package pywin32
import win32con
import win32gui_struct
import configparser
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui



class MainClass(object):
  def __init__(self):
    self._reset()
    self._readconf()
    
  def _reset(self):
    self.showname       = "GifTray"
    self.name           = "giftray"
    if hasattr(self, "avail"):
      for i in self.avail:
        if hasattr(i, "destroy"): i.destroy(i)
      del self.avail
    self.avail          = []
    if hasattr(self, "error"):
      del self.error
    self.error          = []
    if hasattr(self, "install"):
      del self.install
    self.install        = []
    self.conf           = os.getenv('USERPROFILE')+'/'+self.name+'/'+self.name+".conf"
    if hasattr(self, "icos"):
      del self.icos
    self.icos           = []
    self.color          = "blue"
    self.ico_default    = "default_default"
    self.ico_empty      = "default_empty"

  def _readconf(self):
    config = configparser.ConfigParser()
    if os.path.isfile(self.conf) :
        config.read(self.conf)
    elif os.path.isfile(os.getcwd()+'/'+self.name+".conf") :
        config.read(os.getcwd()+'/'+self.name+".conf")
    elif os.path.isfile(os.getcwd()+'/conf/'+self.name+".conf") :
        config.read(os.getcwd()+'/conf/'+self.name+".conf")
    elif os.path.isfile(os.getcwd()+'/../../conf/'+self.name+'.conf') :
        config.read(os.getcwd()+'/../../conf/'+self.name+'.conf')
    else :
        return 1
    print (config.sections())
    #config.write()
    return 0


if __name__ == '__main__':
  #import itertools, glob
  MainClass()
  print('end prog')
