import logging
from PyQt5 import QtWidgets
import zad.pyuic.mainwindow
import zad.models.main

mainWindow = None

l = logging.getLogger(__name__)

class ZaMainWindow(QtWidgets.QMainWindow,zad.pyuic.mainwindow.Ui_mainWindow):
    def __init__(self):
        super(ZaMainWindow,self).__init__()
        self.setupUi(self)


def setup():
    global mainWindow

    mainWindow = ZaMainWindow()
    model = zad.models.main.ZoneModel()
    statusBar = mainWindow.statusbar
    view = mainWindow.maintableView
    view.setColumnWidth(0, 200)
    view.setColumnWidth(1, 40)
    view.setColumnWidth(2, 40)
    view.setColumnWidth(3, 400)
    hh = view.horizontalHeader()
    hh.setStretchLastSection(True)
    hh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    zad.models.main.loadZones()
    ##zad.models.main.loadZones()
    ##zad.models.main.loadZones()
    statusBar.showMessage('Zone loaded')
    view.setModel(model)
    mainWindow.show()
    l.debug('After mw.show')
    return

