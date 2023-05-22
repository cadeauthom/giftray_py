import sys
#setup.py GiftTray GifTray.py ../build/icons/giftray.ico

def help():
    print("Usage sys.argv[0] [Name] [Main Python] [icon]")
    exit(1)

project=''
script=''
icon=''
includes=[]
includefiles=[]
new_argv=[]
for i in sys.argv:
    if i.startswith("--setup-project="):
        project=i.split('=')[1]
    elif i.startswith("--setup-script="):
        script=i.split('=')[1]
    elif i.startswith("--setup-icon="):
        icon=i.split('=')[1]
    elif i.startswith("--setup-include="):
        includes+=(i.split('=')[1]).split(',')
    elif i.startswith("--setup-include-files="):
        includefiles+=(i.split('=')[1]).split(',')
    else:
        new_argv.append(i)

sys.argv = new_argv

if (not project
 or not script
 or not icon
 or not includes
 or not includefiles):
    help()

cfg='''
[metadata]
name = PROJECT
version = 0.1
description = PROJECT
#Tray and Hotkeys for custom shortcuts and commands
[build_exe]
#zip_include_packages = encodings,PySide6
excludes = colorama,curses,distutils,email,html,http,idna,lib2to3,pip,pydoc_data,pywin32_system32,test,unittest,wheel,xml,xmlrpc
packages = clicknium,PyQt6.QtGui,PyQt6.QtWidgets,configparser,copy,ctypes,datetime,functools,inspect,io,logging,natsort,notifypy,os,posixpath,psutil,re,shutil,signal,subprocess,sys,threading,time,trace,win32api,win32con,win32gui,win32process,winxpgui
includes = INCLUDES
include_files = INCLUDEFILES
optimize = 2
[bdist_msi]
all_users = yes
initial_target_dir = [ProgramFilesFolder]\\PROJECT
install_icon = ICON
upgrade_code = {a61f7248-dbf5-453c-aa87-20d7f9d70c4e}
'''
cfg = cfg.replace('PROJECT',project)
cfg = cfg.replace('INCLUDEFILES',','.join(includefiles))
cfg = cfg.replace('INCLUDES',','.join(includes))
cfg = cfg.replace('ICON',icon)

with open('setup.cfg','w') as file:
    file.write(cfg)

from cx_Freeze import setup, Executable
# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None
setup(executables=[Executable(
                    script,
                    base=base,
                    icon=icon
                    )])
