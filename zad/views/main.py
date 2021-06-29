import logging
from PyQt5 import QtCore, QtWidgets
import zad.pyuic.mainwindow
import zad.models.main
import zad.models.settings

mainWindow = None

l = logging.getLogger(__name__)

class ZaMainWindow(QtWidgets.QMainWindow,zad.pyuic.mainwindow.Ui_mainWindow):
    def __init__(self, parent=None):
        self.settings = None

        super(ZaMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def readSettings(self):
        self.settings: QtCore.QSettings = zad.models.settings.settings
        geometry: QtCore.QByteArray = self.settings.value("geometry",
                                                          QtCore.QByteArray()).toByteArray()
        if not geometry:
            availableGeometry: QtCore.QRect = self.screen.availableGeometry()
            self.resize(availableGeometry.width() / 3, availableGeometry.height() / 2)
            self.move((availableGeometry.width() - self.width()) / 2,
                        (availableGeometry.height() - self.height()) / 2)
        else:
            self.restoreGeometry(geometry)

    def writeSettings(self):
        self.settings.setValue("geometry", self.saveGeometry())

    def connectSignalsSlots(self):
        ##self.action_Exit.triggered.connect(self.close)
        ##self.action_About.triggered.connect(self.about)
        ##self.action_Settings.triggered.connect(self.about)
        pass

    def exit(self):
        pass

    def about(self):
        QtWidgets.QMessageBox.about(self, "zad - DNS zone adminsitration tool",
                            "<p>Version {}</p>".format(zad.get_version()))



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

