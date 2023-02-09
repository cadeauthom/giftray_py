import sys
from cx_Freeze import setup, Executable
# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None
setup(executables=[Executable(
                    "GifTray.py",
#"src/icon.py",
                    base=base,
                    icon="../build/icons/giftray.ico"
                    )])
