import PyQt6.QtGui
import PyQt6.QtWidgets
import functools
import sys

app = PyQt6.QtWidgets.QApplication([])
app.setQuitOnLastWindowClosed(False)

# Create the icon
icon = PyQt6.QtGui.QIcon("./dist/giftray/icons/red/windows_MuteUnmute2.ico")
print(icon.availableSizes ()==[])
icon = PyQt6.QtGui.QIcon(sys.executable)
print(icon.availableSizes ()==[])

def act(s):
    print(s)
    return

# Create the tray
tray = PyQt6.QtWidgets.QSystemTrayIcon()
tray.setIcon(icon)
tray.setToolTip("System Tray Management")
tray.setVisible(True)

# Create the menu
menu = PyQt6.QtWidgets.QMenu()
action = PyQt6.QtGui.QAction("A menu item")
menu.addAction(action)

action2 = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon("./dist/giftray/icons/red/windows_MuteUnmute.ico"), "With image menu")
#action2.setObjectName('action to print')
action2.triggered.connect(functools.partial(act, 'action to print'))
menu.addAction(action2)

menu.addSeparator()
# Add a Quit option to the menu.
quit = PyQt6.QtGui.QAction("Quit")
quit.triggered.connect(app.quit)
menu.addAction(quit)

# Add the menu to the tray
tray.setContextMenu(menu)

class Window(PyQt6.QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        icons = sorted([attr for attr in dir(PyQt6.QtWidgets.QStyle.StandardPixmap) if attr.startswith("SP_")])
        layout = PyQt6.QtWidgets.QGridLayout()

        for n, name in enumerate(icons):
            btn = PyQt6.QtWidgets.QPushButton(name)

            pixmapi = getattr(PyQt6.QtWidgets.QStyle.StandardPixmap, name)
            icon = self.style().standardIcon(pixmapi)
            btn.setIcon(icon)
            layout.addWidget(btn, int(n/4), int(n%4))

        self.setLayout(layout)



w = Window()
w.show()


app.exec()
