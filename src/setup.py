import sys
from cx_Freeze import setup, Executable

#setup.py GifTray.py ../build/icons/giftray.ico

if len(sys.argv) > 1:
    script=sys.argv[1]
else:
    print("Python main script not defined as first option")
if len(sys.argv) > 2:
    icon=sys.argv[2]

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None
setup(executables=[Executable(
                    script,
                    base=base,
                    icon=icon
                    )])
