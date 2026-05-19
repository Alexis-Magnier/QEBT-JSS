import sys
from .MainWindow import MainWindow
from .AppContext import AppContext

from PyQt5 import QtCore, QtWidgets

def main():

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('GTK+')
    
    ctx = AppContext()

    window = MainWindow(ctx)

    window.show()
    result = app.exec_()
    window.closing()

    sys.exit(result)