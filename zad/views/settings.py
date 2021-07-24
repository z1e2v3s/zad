import logging
import pprint

from PyQt5 import QtWidgets, QtCore

import zad.app
import zad.pyuic.settings
import zad.models.main
import zad.models.settings


class ZaSettinsDialog(QtWidgets.QDialog,zad.pyuic.settings.Ui_settingsTabWidget):
    def __init__(self):
        super(ZaSettinsDialog,self).__init__()
        self.setupUi(self)
        self.readSettings()
        self.setListViews = []

    def addSetListView(self,slv):
        self.setListViews.append(slv)

    def readSettings(self):
        if zad.prefs._settings.contains('settings_window/size'):
            self.resize(zad.prefs._settings.value('settings_window/size'))
            self.move(zad.prefs._settings.value('settings_window/pos'))

    def writeSettings(self):
        zad.prefs._settings.setValue("settings_window/size", self.size())
        zad.prefs._settings.setValue("settings_window/pos", self.pos())

    def closeEvent(self, event: QtCore.QEvent):
        self.writeSettings()
        zad.prefs.sync()
        event.accept()

sc: QtCore.QSettings = None
sd: ZaSettinsDialog = None
l = logging.getLogger(__name__)

@QtCore.pyqtSlot()
def showSettings():
    global sd
    sd.show()
    ##sd.raise()


class SetListsView(QtCore.QObject):

    def __init__(self,
                 listPrefName: str,
                 listWidget: QtWidgets.QListWidget,
                 lineEdit: QtWidgets.QLineEdit,
                 minusButton: QtWidgets.QPushButton,
                 plusButton: QtWidgets.QPushButton,
                 revertButton: QtWidgets.QPushButton,
                 okButton: QtWidgets.QPushButton,
                 
                 parent=None):

        super(SetListsView, self).__init__(parent)

        self.listPrefName = listPrefName
        self.listWidget = listWidget
        self.listWidget.setSortingEnabled(True)
        self.getPrefs()
        if self.prefs:
            self.listWidget.insertItems(0, self.prefs)
            self.listWidget.clearSelection()
        self.lineEdit = lineEdit
        self.minusButton = minusButton
        self.minusButton.setDisabled(True)
        self.plusButton = plusButton
        self.plusButton.setDisabled(True)
        self.revertButton = revertButton
        self.revertButton.setDisabled(True)
        self.okButton = okButton
        self.okButton.setDisabled(True)

        self.connect_signals()
        
        self.preservedText = ''     # while editing an existing list entry
        self.row: int = None
        
    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def onListItemClicked(self, item):
        if item.text():                         # a row has been selected
            if self.listWidget.selectedItems():
                self.lineEdit.setText(item.text())
                self.preservedText = item.text()
                self.row = self.listWidget.currentRow()
                self.minusButton.setDisabled(False)
                self.minusButton.setDefault(True)
                self.plusButton.setDefault(False)
                self.revertButton.setDisabled(True)
                self.okButton.setDisabled(True)
                self.okButton.setDefault(False)
            else:                                   # no row selected
                self.lineEdit.setText('')
                self.preservedText = ''
                self.minusButton.setDisabled(True)
                self.plusButton.setDisabled(True)
                self.plusButton.setDefault(False)
                self.revertButton.setDisabled(True)
                self.okButton.setDisabled(True)
                self.okButton.setDefault(False)

    @QtCore.pyqtSlot(str)
    def onEdited(self, checked):
        if self.preservedText:      # modifying existing row
            self.plusButton.setDisabled(True)
            self.plusButton.setDefault(False)
            self.minusButton.setDisabled(True)
            self.revertButton.setDisabled(False)

            self.okButton.setDisabled(False)
            self.okButton.setDefault(True)
        else:                       # new row may be added with "+"
            self.minusButton.setDisabled(True)
            self.revertButton.setDisabled(False)
            self.okButton.setDisabled(True)
            self.okButton.setDefault(False)

            self.plusButton.setDisabled(False)
            self.plusButton.setDefault(True)

    @QtCore.pyqtSlot()
    def onEndEdited(self):
        ##self.onOK(False)
        pass

    @QtCore.pyqtSlot(bool)
    def onMinus(self, checked):
        self.delPref(self.preservedText)
        self.listWidget.takeItem(self.listWidget.currentRow())
        self.lineEdit.setText('')
        self.preservedText = ''
        self.minusButton.setDisabled(True)

    @QtCore.pyqtSlot(bool)
    def onPlus(self, checked):
        text = self.lineEdit.text()
        if not self.prefs or not text in self.prefs:
            self.addPref(self.lineEdit.text())
            self.listWidget.addItem(text)
            self.plusButton.setDisabled(True)
        else:
            zad.app.application.beep()

    @QtCore.pyqtSlot(bool)
    def onRevert(self, checked):
        self.lineEdit.setText(self.preservedText)
        self.revertButton.setDisabled(True)
        self.okButton.setDisabled(True)
        self.okButton.setDefault(False)

    @QtCore.pyqtSlot(bool)
    def onOK(self, checked):
        row =self.listWidget.currentRow()
        if row:                                             # may called on defocus w/o current row
            self.setPref(row, self.lineEdit.text())
            self.listWidget.takeItem(self.listWidget.currentRow())
            self.listWidget.addItem(self.lineEdit.text())
            self.lineEdit.setText('')
            self.preservedText = ''
            self.plusButton.setDisabled(True)
            self.minusButton.setDisabled(True)
            self.revertButton.setDisabled(True)
            self.okButton.setDisabled(True)
            self.okButton.setDefault(False)

    def connect_signals(self):
        self.listWidget.itemClicked.connect(self.onListItemClicked)
        self.lineEdit.textEdited.connect(self.onEdited)
        self.lineEdit.editingFinished.connect(self.onEndEdited)
        self.minusButton.clicked.connect(self.onMinus)
        self.plusButton.clicked.connect(self.onPlus)
        self.revertButton.clicked.connect(self.onRevert)
        self.okButton.clicked.connect(self.onOK)

    def getPrefs(self):
        self.prefs = zad.prefs.get_net_list(self.listPrefName)

    def addPref(self, value):
        self.getPrefs()
        self.prefs.append(value)
        self.updatePrefs()

    def setPref(self, index, value):
        self.getPrefs()
        self.prefs[index] = value
        self.updatePrefs()

    def delPref(self, value):
        self.getPrefs()
        self.prefs.remove(value)
        self.updatePrefs()

    def updatePrefs(self):
        zad.prefs._updateNetList(self.listPrefName, self.prefs)

    def printSettings(self, place):
        global sc
        print('Settings of list at {}:\n{}'.format(place, self.getPrefs()))
        print('Settings at {}:\n{}'.format(place, pprint.pprint(sc.as_dict())))


def setup():
    global settingsDialog, sd

    sd = ZaSettinsDialog()

    sd.addSetListView(SetListsView(
        "ip4_nets",
        sd.iPv4ListWidget,
        sd.iPv4LineEdit,
        sd.iPv4MinusButton,
        sd.iPv4PlusButton,
        sd.iPv4RevertButton,
        sd.iPv4OkButton)
    )

    sd.addSetListView(SetListsView(
        "ip6_nets",
        sd.iPv6ListWidget,
        sd.iPv6LineEdit,
        sd.iPv6MinusButton,
        sd.iPv6PlusButton,
        sd.iPv6RevertButton,
        sd.iPv6OkButton)
    )

    sd.addSetListView(SetListsView(
        "ignored_nets",
        sd.ignoredListWidget,
        sd.ignoredLineEdit,
        sd.ignoredMinusButton,
        sd.ignoredPlusButton,
        sd.ignoredRevertButton,
        sd.ignoredOkButton)
    )

