import logging
import pprint

from PyQt5 import QtWidgets, QtCore
import pyqtconfig

import zad.pyuic.settings
import zad.models.main
import zad.models.settings


class ZaSettinsDialog(QtWidgets.QDialog,zad.pyuic.settings.Ui_settingsTabWidget):
    def __init__(self):
        super(ZaSettinsDialog,self).__init__()
        self.setupUi(self)
        self.setListViews = []

    def addSetListView(self,slv):
        self.setListViews.append(slv)



sc:pyqtconfig.QSettingsManager = None
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
        self.prefs = []
        self.row: int = None
        
    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def onListItemClicked(self, item):
        if item.text():
            self.lineEdit.setText(item.text())
            self.preservedText = item.text()
            self.row = self.listWidget.currentRow()
            self.minusButton.setDisabled(False)
            self.plusButton.setDisabled(True)
            self.revertButton.setDisabled(True)
            self.okButton.setDisabled(True)

    @QtCore.pyqtSlot(str)
    def onEdited(self, checked):
        if self.preservedText:      # modifying existing row
            self.plusButton.setDisabled(True)
            self.minusButton.setDisabled(True)
            self.revertButton.setDisabled(False)
            self.okButton.setDisabled(False)
        else:                       # new row may be added with "+"
            self.plusButton.setDisabled(False)
            self.minusButton.setDisabled(True)
            self.revertButton.setDisabled(False)
            self.okButton.setDisabled(True)

    @QtCore.pyqtSlot()
    def onEndEdited(self):
        self.onOK(False)

    @QtCore.pyqtSlot(bool)
    def onMinus(self, checked):
        self.delPref(self.preservedText)
        self.lineEdit.setText('')
        self.preservedText = ''
        self.minusButton.setDisabled(True)

    @QtCore.pyqtSlot(bool)
    def onPlus(self, checked):
        self.addPref(self.lineEdit.text())
        self.plusButton.setDisabled(True)
        self.printSettings('End plus')

    @QtCore.pyqtSlot(bool)
    def onRevert(self, checked):
        self.lineEdit.setText(self.preservedText)
        self.revertButton.setDisabled(True)
        self.okButton.setDisabled(True)

    @QtCore.pyqtSlot(bool)
    def onOK(self, checked):
        row =self.listWidget.currentRow()
        if row:                                             # may called on defocus w/o current row
            self.setPref(row, self.lineEdit.text())
            self.lineEdit.setText('')
            self.preservedText = ''
            self.plusButton.setDisabled(True)
            self.minusButton.setDisabled(True)
            self.revertButton.setDisabled(True)
            self.okButton.setDisabled(True)

    def connect_signals(self):
        self.listWidget.itemClicked.connect(self.onListItemClicked)
        self.lineEdit.textEdited.connect(self.onEdited)
        self.lineEdit.editingFinished.connect(self.onEndEdited)
        self.minusButton.clicked.connect(self.onMinus)
        self.plusButton.clicked.connect(self.onPlus)
        self.revertButton.clicked.connect(self.onRevert)
        self.okButton.clicked.connect(self.onOK)

    def getPrefs(self):
        self.prefs = sc.get(self.listPrefName)
        return

    def addPref(self, value):
        self.getPrefs()
        self.prefs.append(value)
        sc.set(self.listPrefName, self.prefs)
        self.printSettings('End addPref')

    def setPref(self, index, value):
        self.prefs[index] = value
        sc.set(self.listPrefName, self.prefs)

    def delPref(self, value):
        self.getPrefs()
        self.prefs.remove(value)
        sc.set(self.listPrefName, self.prefs)
    def updatePrefs(self):
        pass
    
    def printSettings(self, place):
        global sc
        print('Settings of list at {}:\n{}'.format(place, self.getPrefs()))
        print('Settings at {}:\n{}'.format(place, pprint.pprint(sc.as_dict())))

def setup():
    global settingsDialog, sc, sd

    sc = zad.models.settings.conf
    sd = ZaSettinsDialog()

    sc.add_handler("gen/master_server", sd.masterServerLineEdit)
    sc.add_handler("gen/ddns_key_file", sd.ddnsKeyFileLineEdit)
    sc.add_handler("gen/ns_for_axfr", sd.serverForZoneTransferLineEdit)
    sc.add_handler("gen/initial_domain", sd.initialDomainLineEdit)
    sc.add_handler("gen/default_ip4_prefix", sd.defaultPrefixIPv4LineEdit)
    sc.add_handler("gen/default_ip6_prefix", sd.defaultPrefixIPv6LineEdit)
    sc.add_handler("gen/log_file", sd.logfileLineEdit)
    sc.add_handler("gen/debug", sd.debugCheckBox)
    sc.add_handler("gen/ip4_nets", sd.iPv4ListWidget)
    sc.add_handler("gen/ip6_nets", sd.iPv6ListWidget)
    sc.add_handler("gen/ignored_nets", sd.ignoredListWidget)

    sd.addSetListView(SetListsView(
        "gen/ip4_nets",
        sd.iPv4ListWidget,
        sd.iPv4LineEdit,
        sd.iPv4MinusButton,
        sd.iPv4PlusButton,
        sd.iPv4RevertButton,
        sd.iPv4OkButton)
    )

    sd.addSetListView(SetListsView(
        "gen/ip6_nets",
        sd.iPv6ListWidget,
        sd.iPv6LineEdit,
        sd.iPv6MinusButton,
        sd.iPv6PlusButton,
        sd.iPv6RevertButton,
        sd.iPv6OkButton)
    )

    sd.addSetListView(SetListsView(
        "gen/ignored_nets",
        sd.ignoredListWidget,
        sd.ignoredLineEdit,
        sd.ignoredMinusButton,
        sd.ignoredPlusButton,
        sd.ignoredRevertButton,
        sd.ignoredOkButton)
    )

