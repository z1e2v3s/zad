import asyncio
import logging
from PyQt5 import QtCore, QtWidgets
import zad.pyuic.mainwindow
import zad.models.axfr
import zad.models.main
import zad.models.settings
import zad.views.settings

mainWindow = None
statusBar = None

l = logging.getLogger(__name__)

class ZaMainWindow(QtWidgets.QMainWindow,zad.pyuic.mainwindow.Ui_mainWindow):
    set_text_signal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        self.settings = None

        super(ZaMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.startThread()

    def startThread(self):
        loop = asyncio.get_event_loop()
        self.asyciothread = zad.models.axfr.RunThread(loop)
        self.thread = QtCore.QThread()
        self.asyciothread.moveToThread(self.thread)

        self.set_text_signal.connect(self.asyciothread.set_text_slot)
        self.asyciothread.zone_loaded.connect(self.receivefromthread)
        self.thread.started.connect(self.asyciothread.work)

        self.thread.start()

    @QtCore.pyqtSlot(str)
    def receivefromthread(self, s):
        statusBar.showMessage('{} loaded'.format(s))

    ##def sendtotask(self):
    ##    self.set_text_signal.emit("Task: Configured")

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

    def exit(self):
        pass

    def about(self):
        QtWidgets.QMessageBox.about(self, None,
                "<p>zad - DNS zone adminsitration tool</p><p>Version {}</p>".format(zad.get_version()))

    def connectActions(self):
        self.actionAbout.triggered.connect(self.about)
        self.actionSettings.triggered.connect(zad.views.settings.showSettings)


def setup():
    global mainWindow, statusBar

    mainWindow = ZaMainWindow()
    mainWindow.connectActions()
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
    ##zad.models.main.loadZones()
    ##zad.models.main.loadZones()
    ##zad.models.main.loadZones()
    statusBar.showMessage('Loading zones . . .')
    view.setModel(model)
    mainWindow.show()
    l.debug('After mw.show')
    return

