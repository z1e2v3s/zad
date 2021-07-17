import asyncio
import logging
from PyQt5 import QtCore, QtWidgets
import zad.pyuic.mainwindow
import zad.models.axfr
import zad.models.main
import zad.models.settings
import zad.views.settings
import zad.views.tables

mainWindow = None
statusBar: QtWidgets.QStatusBar = None

l = logging.getLogger(__name__)

class ZaMainWindow(QtWidgets.QMainWindow,zad.pyuic.mainwindow.Ui_mainWindow):
    set_text_signal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        self.previous_status_text = ''

        super(ZaMainWindow,self).__init__(parent)
        self.setupUi(self)
        zad.views.tables.setup(self)
        self.startThread()

    def startThread(self):
        loop = asyncio.get_event_loop()
        self.asynciothread = zad.models.axfr.RunThread(loop)
        self.thread = QtCore.QThread()
        self.asynciothread.moveToThread(self.thread)

        self.set_text_signal.connect(self.asynciothread.set_text_slot)
        self.asynciothread.axfr_message.connect(self.receive_status_bar_message)
        self.asynciothread.zone_loaded_message.connect(self.receive_zone_loaded_message)
        self.thread.started.connect(self.asynciothread.work)

        self.thread.start()

    @QtCore.pyqtSlot(str)
    def receive_status_bar_message(self, msg):
        statusBar.showMessage('{}{}{}'.format(
            self.previous_status_text,
            ' --- ' if self.previous_status_text else '',
            msg))
        self.previous_status_text = msg

    @QtCore.pyqtSlot(str)
    def receive_zone_loaded_message(self, zone_name):
        return zad.views.tables.zone_loaded(zone_name)
        
    ##def sendtotask(self):
    ##    self.set_text_signal.emit("Task: Configured")

    def closeEvent(self, event: QtCore.QEvent):
        self.writeSettings()
        event.accept()
        del zad.models.settings.settings

    def readSettings(self):
        geometry: QtCore.QByteArray = zad.models.value("geometry",
                                                          QtCore.QByteArray()).toByteArray()
        if not geometry:
            availableGeometry: QtCore.QRect = self.screen.availableGeometry()
            self.resize(availableGeometry.width() / 3, availableGeometry.height() / 2)
            self.move((availableGeometry.width() - self.width()) / 2,
                        (availableGeometry.height() - self.height()) / 2)
        else:
            self.restoreGeometry(geometry)

    def writeSettings(self):
        zad.models.settings.settings.setValue("geometry", self.saveGeometry())

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
    statusBar = mainWindow.statusbar
    mainWindow.show()
    l.debug('After mw.show')
    return

