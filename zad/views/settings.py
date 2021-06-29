import logging
from PyQt5 import QtWidgets, uic
import zad.pyuic.mainwindow
import zad.models.main

settingsDialog = None

l = logging.getLogger(__name__)

class ZaSettinsDialog(QtWidgets.QMainWindow,zad.pyuic.mainwindow.Ui_mainWindow):
    def __init__(self):
        super(ZaMainWindow,self).__init__()
        self.setupUi(self)


class ZaSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("../Designer/settings.ui", self)

def setup():
    global settingsDialog

    settingsDialog = ZaSettinsDialog()

