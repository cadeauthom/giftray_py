from __future__ import unicode_literals

# pywin32 imports
import pywintypes
import win32ui
import win32gui
import win32con
import win32api
import win32file

# ctypes configuring. pywin32 has no a lot of required functions
import ctypes
import ctypes.util
import os

PATH=os.getcwd()+"/upx-3.96-win64/upx.exe"
PATH=os.getcwd()+"/build/giftray/giftray.exe"
print(PATH)

def extract(rec):
    try:
        hicon = win32gui.CreateIconFromResource(rec, True)
    except pywintypes.error as error:
        # Check on appropriate error
        if error.winerror != 6:
            raise

        print("Resource %2d isn't .ico, extract" % icon_name)
        # This part almost identical to C++ 
        hResInfo = ctypes.windll.kernel32.FindResourceW(hlib, icon_name, win32con.RT_ICON)
        size = ctypes.windll.kernel32.SizeofResource(hlib, hResInfo)
        mem_pointer = ctypes.windll.kernel32.LockResource(rec)

        # And this is some differ (copy data to Python buffer)
        binary_data = (ctypes.c_ubyte * size)()
        libc.memcpy(binary_data, mem_pointer, size)

        # Save it
        with open("Resource_%s.png" % icon_name, "wb") as extract_file:
            extract_file.write(bytearray(binary_data))
    else:
        info = win32gui.GetIconInfo(hicon)
        bminfo = win32gui.GetObject(info[3])
        print("Resource %2d is .ico: 0x%08X -> %d %d " % 
                  (icon_name, hicon, bminfo.bmWidth, bminfo.bmHeight))
        print(bminfo)
        print(info)


try:
    hlib = win32api.LoadLibrary(PATH)
    icon_names = win32api.EnumResourceNames(hlib, win32con.RT_ICON)
    for icon_name in icon_names:
        rec = win32api.LoadResource(hlib, win32con.RT_ICON, icon_name)
        extract(rec)

except pywintypes.error as error:
    print( "ERROR: %s" % error.strerror)
    raise
