#Code generated by ChatGPT
import struct
import pywintypes

def build_icon_dll():
    icon_path='../build/icons/red/'
    # Define the resource data for the two icons
    icon1_data = open(icon_path+"giftray-0.ico", "rb").read()
    icon2_data = open(icon_path+"giftray-1.ico", "rb").read()
    data = (
        b"\x00\x00\x01\x00\x01\x00\x10\x10\x10\x00\x01\x00\x04\x00"
        + struct.pack("<L", len(icon1_data))
        + icon1_data
        + b"\x00\x00\x01\x00\x01\x00\x10\x10\x10\x00\x01\x00\x04\x00"
        + struct.pack("<L", len(icon2_data))
        + icon2_data
    )

    # Write the resource data to a DLL file
    hdll = pywintypes.HMODULE(0)
    hres = win32api.BeginUpdateResource("icon_dll.dll", False)
    win32api.UpdateResource(hres, win32con.RT_ICON, 1, data)
    win32api.EndUpdateResource(hres, False)

build_icon_dll()