import logging
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



sd: ZaSettinsDialog = None
l = logging.getLogger(__name__)

@QtCore.pyqtSlot()
def showSettings():
    global sd
    sd.show()


class SetListsView(QtCore.QObject):

    def __init__(self,
                 listWidget: QtWidgets.QListWidget,
                 lineEdit: QtWidgets.QLineEdit,
                 minusButton: QtWidgets.QPushButton,
                 plusButton: QtWidgets.QPushButton,
                 revertButton: QtWidgets.QPushButton,
                 okButton: QtWidgets.QPushButton,
                 
                 parent=None):

        super(SetListsView, self).__init__(parent)

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
        
        self.preservedList = []
        self.preservedText = ''     # while editing an existing list entry
        
    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def onListItemClicked(self, item):
        if item.text():
            self.lineEdit.setText(item.text())
            self.preservedText = item.tex()
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
        self.listWidget.takeItem(self.listWidget.currentRow)
        self.lineEdit.setText('')
        self.preservedText = ''
        self.minusButton.setDisabled(True)

    @QtCore.pyqtSlot(bool)
    def onPlus(self, checked):
        self.listWidget.addItem(self.lineEdit.text())
        self.plusButton.setDisabled(True)

    @QtCore.pyqtSlot(bool)
    def onRevert(self, checked):
        self.lineEdit.setText(self.preservedText)
        self.revertButton.setDisabled(True)
        self.okButton.setDisabled(True)

    @QtCore.pyqtSlot(bool)
    def onOK(self, checked):
        if self.listWidget.currentRow():    # may called on defocus w/o current row
            self.listWidget.takeItem(self.listWidget.currentRow())
            self.listWidget.addItem(self.lineEdit.text())
            self.lineEdit.setText('')
            self.preservedText = ''
            self.minusButton.setDisabled(True)
            self.minusButton.setDisabled(True)
            self.revertButton.setDisabled(False)
            self.okButton.setDisabled(False)

    def connect_signals(self):
        self.listWidget.itemClicked.connect(self.onListItemClicked)
        self.lineEdit.textEdited.connect(self.onEdited)
        self.lineEdit.editingFinished.connect(self.onEndEdited)
        self.minusButton.clicked.connect(self.onMinus)
        self.plusButton.clicked.connect(self.onPlus)
        self.revertButton.clicked.connect(self.onRevert)
        self.okButton.clicked.connect(self.onOK)



def setup():
    global settingsDialog, sd

    sc: pyqtconfig.QSettingsManager = zad.models.settings.conf
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
        sd.iPv4ListWidget,
        sd.iPv4LineEdit,
        sd.iPv4MinusButton,
        sd.iPv4PlusButton,
        sd.iPv4RevertButton,
        sd.iPv4OkButton)
    )

    sd.addSetListView(SetListsView(
        sd.iPv6ListWidget,
        sd.iPv6LineEdit,
        sd.iPv6MinusButton,
        sd.iPv6PlusButton,
        sd.iPv6RevertButton,
        sd.iPv6OkButton)
    )

    sd.addSetListView(SetListsView(
        sd.ignoredListWidget,
        sd.ignoredLineEdit,
        sd.ignoredMinusButton,
        sd.ignoredPlusButton,
        sd.ignoredRevertButton,
        sd.ignoredOkButton)
    )

