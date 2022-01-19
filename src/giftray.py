



import os
import sys
import win32api         # package pywin32
import win32con
import win32gui_struct
import keyboard
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

#keyboard.add_hotkey('ctrl + shift + z', print, args =('Hotkey', 'Detected')) 
class MainClass(object):
  def __init__(self):
    self._reset()
    self._readconf()
    print ("end")
    
  def _reset(self):
    self.name="GifTray"
    if hasattr(self, "avail"):
      for i in self.avail:
        if hasattr(i, "destroy"): i.destroy(i)
      del self.avail
    self.avail=[]
    if hasattr(self, "error"):
      del self.error
    self.error=[]
    if hasattr(self, "install"):
      del self.install
    self.install=[]
    self.conf=""
    self.admin_conf=""
    if hasattr(self, "icos"):
      del self.icos
    self.icos=[]
    self.color="blue"
    self.ico_default="default_default"
    self.ico_empty="default_empty"

  def _readconf(self):
    return 0


if __name__ == '__main__':
  #import itertools, glob
  MainClass()
  print('end prog')
