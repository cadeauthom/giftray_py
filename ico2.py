
import win32ui
import win32gui
import win32con
import win32api

ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
path="c:/windows/system32/shell32.dll"
path="build/giftray/icons/giftray.ico"
path="c:/windows/system32/imageres.dll"
path="test.ico"

for i in range(win32gui.ExtractIconEx(path,-1)):
    large, small =win32gui.ExtractIconEx(path,i)
    for j in range(len(small)):
        hdc = win32ui.CreateDCFromHandle( win32gui.GetDC(0) )
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap( hdc, ico_x, ico_x )
        hdc = hdc.CreateCompatibleDC()
        
        hdc.SelectObject( hbmp )
        hdc.DrawIcon( (0,0), small[j] )
        hbmp.SaveBitmapFile( hdc, "save"+str(j)+"-"+str(i)+".bmp" )
        win32gui.DestroyIcon(small[0])
        win32gui.DestroyIcon(large[0])
