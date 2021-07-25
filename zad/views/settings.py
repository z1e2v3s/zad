import logging
import pprint

from PyQt5 import QtWidgets, QtCore

import zad.app
import zad.pyuic.settings
import zad.models.main
import zad.models.settings



class PrefLineEditView(QtCore.QObject):

    def __init__(self,
                 lineEdit: QtWidgets.QLineEdit,
                 prefName: str):
        super(PrefLineEditView, self).__init__()
        self.lineEdit: QtWidgets.QLineEdit = lineEdit
        self.prefName: str = prefName
        self.preservedText = ''

    def readPref(self):
        self.preservedText = str(getattr(zad.prefs, self.prefName))
        self.lineEdit.setText(self.preservedText)

    def writePref(self):
        self.preservedText = self.lineEdit.text()
        setattr(zad.prefs, self.prefName, self.preservedText)

    def revert(self):
        self.lineEdit.setText(self.preservedText)


class ZaSettingsDialog(QtWidgets.QDialog,zad.pyuic.settings.Ui_settingsTabWidget):
    def __init__(self):
        super(ZaSettingsDialog, self).__init__()
        self.setupUi(self)
        self.readSettings()
        self.lineEditViews = []
        self.setListViews = []

        self.init_pane_1()
        self.connect_signals()

    @QtCore.pyqtSlot(str)
    def onEdited(self, checked):
        self.OkButton.setDisabled(False)
        self.OkButton.setDefault(True)
        self.revertButton.setDisabled(False)

    @QtCore.pyqtSlot(int)
    def onCheckBoxChanged(self, state):
        self.OkButton.setDisabled(False)
        self.OkButton.setDefault(True)
        self.revertButton.setDisabled(False)

    @QtCore.pyqtSlot(bool)
    def onOK(self, checked):
        self.OkButton.setDisabled(True)
        self.revertButton.setDisabled(True)
        for lineEditView in self.lineEditViews:
            lineEditView.writePref()
        self.preservedDebugState = self.debugCheckBox.isChecked()
        zad.prefs.debug = self.preservedDebugState

    @QtCore.pyqtSlot(bool)
    def onRevert(self, checked):
        self.OkButton.setDisabled(True)
        self.revertButton.setDisabled(True)
        for lineEditView in self.lineEditViews:
            lineEditView.revert()
        self.debugCheckBox.setChecked(self.preservedDebugState)

    def init_pane_1(self):
        for lineEdit, prefName in [(self.masterServerLineEdit, 'master_server'),
                                   (self.ddnsKeyFileLineEdit, 'ddns_key_file'),
                                   (self.serverForZoneTransferLineEdit, 'ns_for_axfr'),
                                   (self.initialDomainLineEdit, 'initial_domain'),
                                   (self.defaultPrefixIPv4LineEdit, 'default_ip4_prefix'),
                                   (self.defaultPrefixIPv6LineEdit, 'default_ip6_prefix'),
                                   (self.logfileLineEdit, 'log_file')]:
            plf = PrefLineEditView(lineEdit, prefName)
            self.lineEditViews.append(plf)

        for prefLineEditView in self.lineEditViews:
            prefLineEditView.readPref()

        self.OkButton.setDisabled(True)
        self.revertButton.setDisabled(True)
        self.preservedDebugState = zad.prefs.debug
        self.debugCheckBox.setChecked(self.preservedDebugState)

    def connect_signals(self):
        for lineEditView in self.lineEditViews:
            lineEditView.lineEdit.textEdited.connect(self.onEdited)
        self.debugCheckBox.stateChanged.connect(self.onCheckBoxChanged)
        self.revertButton.clicked.connect(self.onRevert)
        self.OkButton.clicked.connect(self.onOK)

    def addSetListView(self, slv):
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
sd: ZaSettingsDialog = None
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


class Tab1View(QtCore.QObject):
    def __init__(self,
        parent = None):
        super(Tab1View, self).__init__(parent)

        self.preservedText = ''



def setup():
    global settingsDialog, sd

    sd = ZaSettingsDialog()

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

