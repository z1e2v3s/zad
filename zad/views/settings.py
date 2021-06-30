import logging
from PyQt5 import QtWidgets, QtCore
import zad.pyuic.settings
import zad.models.main

settingsDialog = None

l = logging.getLogger(__name__)

class ZaSettinsDialog(QtWidgets.QDialog,zad.pyuic.settings.Ui_settingsTabWidget):
    def __init__(self):
        super(ZaSettinsDialog,self).__init__()
        self.setupUi(self)

@QtCore.pyqtSlot()
def showSettings(self):
      settingsDialog.show()

def setup():
    global settingsDialog

    settingsDialog = ZaSettinsDialog()

