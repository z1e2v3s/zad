from PyQt5 import QtWidgets

import zad.pyuic.mainwindow
import zad.models.main


class ZaMainWindow(QtWidgets.QMainWindow,zad.pyuic.mainwindow.Ui_mainWindow):
    def __init__(self):
        super(ZaMainWindow,self).__init__()
        self.setupUi(self)


def setup():

    mw = ZaMainWindow()
    model = zad.models.main.ZoneModel()
    statusBar = mw.statusbar
    view = mw.maintableView
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
    mw.show()
    print('After mw.show')
    
