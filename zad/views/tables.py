import logging
from PyQt5 import QtCore, QtWidgets

import zad.common
import zad.models.axfr
import zad.models.main
import zad.views.main

l = logging.getLogger(__name__)

mw = None

edit_zone_view = None
zone_view_1 = None
zone_view_2 = None
zone_view_3 = None


def setup(mainWindow):
    global mw
    mw = mainWindow


class ZoneView(QtCore.QObject):

    def __init__(self,
                 zoneBox: QtWidgets.QComboBox,
                 netBox: QtWidgets.QComboBox,
                 tabView: QtWidgets.QTableView,
                 parent=None):
        super(ZoneView, self).__init__(parent)

        self.zoneBox: QtWidgets.QComboBox = zoneBox
        self.netBox: QtWidgets.QComboBox = netBox
        self.tabView = tabView
        self.zoneBoxNames = []
        self.netBoxNames = []
        self.zone = None
        self.net_name = ''              # preserved net name

        self.init_tabView()
        self.connect_signals()

    @QtCore.pyqtSlot(str)
    def zoneBoxSelectionChanged(self, zone_name: str):
        if zone_name:
            self.reload_table(zone_name)

    @QtCore.pyqtSlot(str)
    def netBoxSelectionChanged(self, net_name: str):
        if net_name:
            self.reload_net(net_name)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def tableRowDoubleClicked_slot(self, index):
        if index.isValid:
            edit_zone_view.otherDoubleClicked(self.zone.name, index.row())

    def addZone(self, zone_name):
        ct = cn = None
        if self.zoneBoxNames:
            ct = self.zoneBox.currentText()
        self.zoneBoxNames.append(zone_name)
        self.zoneBoxNames.sort()
        self.zoneBox.clear()
        self.zoneBox.addItems(self.zoneBoxNames)
        if ct:
            self.zoneBox.setCurrentText(ct)


    def reload_table(self, zone_name):
        model = None
        if zone_name:
            self.zone: zad.models.axfr.Zone = zad.models.axfr.Zone.zoneByName(zone_name)
        if self.zone.type in (zad.common.ZTIP4, zad.common.ZTIP6):                      # a net zone
            self.updateNets()
            if not self.net_name:
                return
            if self.net_name in self.zone.nets:             ## FIXME: addNet changed asynchronously?
                model = zad.models.main.ZoneModel(self.zone.nets[self.net_name].data, True)
        else:
            model = zad.models.main.ZoneModel(self.zone.d)
        self.tabView.setModel(model)
        self.zoneBox.setCurrentText(zone_name)

    def updateNets(self):
        """
        Updates netBoxNames from current zone
        """
        self.netBoxNames = list(self.zone.nets.keys())
        if not self.netBoxNames:
            return
        self.netBoxNames.sort()
        self.netBox.clear()
        self.netBox.addItems(self.netBoxNames)
        self.reload_net(self.netBoxNames[0])

    def reload_net(self, net_name):
        if not self.zone or not net_name or self.zone.type not in (
                                                            zad.common.ZTIP4, zad.common.ZTIP6):
            l.info('%% reload_net: premature return. net_name={}, zone={}, type={}'.format(
                                            net_name,
                                            self.zone.name if self.zone else '',
                                            self.zone.type if self.zone else ''))
            return
        if net_name in self.zone.nets:  ## FIXME: addNet changed asynchronously?
            self.net_name = net_name
            model = zad.models.main.ZoneModel(self.zone.nets[self.net_name].data, True)
            self.tabView.setModel(model)
            self.netBox.setCurrentText(net_name)

    def init_tabView(self):
        self.tabView.setColumnWidth(0, 100)
        self.tabView.setColumnWidth(1, 40)
        self.tabView.setColumnWidth(2, 100)
        hh = self.tabView.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def connect_signals(self):
        self.zoneBox.currentTextChanged.connect(self.zoneBoxSelectionChanged)
        self.netBox.currentTextChanged.connect(self.netBoxSelectionChanged)
        self.tabView.doubleClicked.connect(self.tableRowDoubleClicked_slot)



class ZoneEdit(ZoneView):

    def __init__(self,
                 zoneBox: QtWidgets.QComboBox,
                 netBox: QtWidgets.QComboBox,
                 tabView: QtWidgets.QTableView,
                 parent=None):
        super(ZoneView, self).__init__(parent)

        self.zoneBox: QtWidgets.QComboBox = zoneBox
        self.netBox: QtWidgets.QComboBox = netBox
        self.tabView = tabView
        self.zoneBoxNames = []
        self.netBoxNames = []
        self.zone = None
        self.net_name = ''
        self.tableIndex = None

        self.init_tabView()
        self.clearButtons()
        self.connect_signals()


    @QtCore.pyqtSlot(bool)
    def onMinus(self, checked):
        pass

    @QtCore.pyqtSlot(bool)
    def onPlus(self, checked):
        pass

    @QtCore.pyqtSlot(bool)
    def onReset(self, checked):
        mw.buttonOK.setDisabled(True)
        mw.buttonReset.setDisabled(True)
        # restore fields

    @QtCore.pyqtSlot(bool)
    def onOK(self, checked):
        mw.buttonOK.setDisabled(True)
        mw.buttonReset.setDisabled(True)
        # issue change update

    @QtCore.pyqtSlot(str)
    def onEdited(self, text):
        self.edited()

    @QtCore.pyqtSlot()
    def rdataEdited(self):
        self.edited()

    def edited(self):
        mw.buttonOK.setDisabled(False)
        mw.buttonOK.setDefault(True)
        mw.buttonReset.setDisabled(False)

    @QtCore.pyqtSlot(str)
    def zoneBoxSelectionChanged(self, zone_name: str):
        if zone_name:
            self.reload_table(zone_name)

    @QtCore.pyqtSlot(str)
    def netBoxSelectionChanged(self, net_name: str):
        if net_name:
            self.reload_net(net_name)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def tableRowSelected_slot(self, index):
        self.tableIndex = index
        self.loadForm(index)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex, )
    def onSelectionChanged(self, index, oldIndex):
        ##print('QItemSelection={}'.format(sel.indexes))
        self.tableIndex = index
        self.loadForm(index)


    def loadForm(self, index):
        model = self.tabView.model()
        if self.zone.type == zad.common.ZTDOM:
            i = model.createIndex(index.row(), 1)
            mw.nameAddressEdit.setText(model.data(i, QtCore.Qt.DisplayRole))
            i = model.createIndex(index.row(), 2)
            mw.ttlEdit.setText(model.data(i, QtCore.Qt.DisplayRole))
            i = model.createIndex(index.row(), 3)
            mw.typeEdit.setText(model.data(i, QtCore.Qt.DisplayRole))
            i = model.createIndex(index.row(), 4)
            mw.rdataEdit.setText(model.data(i, QtCore.Qt.DisplayRole))
        else:                                                   # net zone, load host field
            i = model.createIndex(index.row(), 0)
            mw.hostLineEdit.setText(model.data(i, QtCore.Qt.DisplayRole))
            i = model.createIndex(index.row(), 1)
            mw.nameAddressEdit.setText(model.data(i, QtCore.Qt.DisplayRole))
            i = model.createIndex(index.row(), 2)
            mw.ttlEdit.setText(model.data(i, QtCore.Qt.DisplayRole))
            i = model.createIndex(index.row(), 3)
            mw.typeEdit.setText(model.data(i, QtCore.Qt.DisplayRole))
            i = model.createIndex(index.row(), 4)
            mw.rdataEdit.setText(model.data(i, QtCore.Qt.DisplayRole))

        mw.buttonM.setDisabled(False)
        mw.buttonM.setDefault(True)
        mw.buttonP.setDefault(False)
        mw.buttonP.setDisabled(True)
        mw.buttonOK.setDisabled(True)
        mw.buttonOK.setDefault(False)

    def clearForm(self):
        mw.hostLineEdit.clear()
        mw.nameAddressEdit.clear()
        mw.ttlEdit.clear()
        mw.typeEdit.clear()
        mw.rdataEdit.clear()

    def clearButtons(self):
        mw.buttonM.setDisabled(True)
        mw.buttonM.setDefault(False)
        mw.buttonP.setDefault(False)
        mw.buttonP.setDisabled(True)
        mw.buttonOK.setDisabled(True)
        mw.buttonOK.setDefault(False)
        mw.buttonReset.setDisabled(True)
        mw.buttonReset.setDefault(False)

    def otherDoubleClicked(self, zone_name, row):
        pass

    def selfSelected(self, zone_name, row):
        pass


    def addZone(self, zone_name):
        ct = cn = None
        if self.zoneBoxNames:
            ct = self.zoneBox.currentText()
            if self.zone.type != zad.common.ZTDOM:
                cn = self.net_name
        self.zoneBoxNames.append(zone_name)
        self.zoneBoxNames.sort()
        self.zoneBox.clear()
        self.zoneBox.addItems(self.zoneBoxNames)
        if ct:
            self.zoneBox.setCurrentText(ct)
        if self.tableIndex:
            self.tabView.selectRow(self.tableIndex.row())
            self.loadForm(self.tableIndex)
    
    def reload_table(self, zone_name):
        model = None
        if zone_name:
            self.zone: zad.models.axfr.Zone = zad.models.axfr.Zone.zoneByName(zone_name)
        if self.zone.type in (zad.common.ZTIP4, zad.common.ZTIP6):                      # a net zone
            self.updateNets()
            if not self.net_name:
                return
            model = zad.models.main.EditZoneModel(self.zone.nets[self.net_name].data, True)
        else:
            model = zad.models.main.EditZoneModel(self.zone.d)
            self.clear_netbox()
        self.tabView.setModel(model)
        self.zoneBox.setCurrentText(zone_name)
        self.clearForm()
        self.clearButtons()

    def reload_net(self, net_name):
        if not self.zone or not net_name or self.zone.type not in (
                                                            zad.common.ZTIP4, zad.common.ZTIP6):
            return
        if net_name in self.zone.nets:  ## FIXME: addNet changed asynchronously?
            self.net_name = net_name
            model = zad.models.main.EditZoneModel(self.zone.nets[self.net_name].data, True)
            self.tabView.setModel(model)
            self.netBox.setCurrentText(net_name)
            self.clearForm()
            self.clearButtons()

    def clear_netbox(self):
        self.netBoxNames = []
        self.net_name = ''
        self.netBox.clear()

    def init_tabView(self):
        self.tabView.setColumnWidth(0, 20)
        self.tabView.setColumnWidth(1, 100)
        self.tabView.setColumnWidth(2, 40)
        self.tabView.setColumnWidth(3, 40)
        self.tabView.setColumnWidth(4, 400)
        hh = self.tabView.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def connect_signals(self):
        self.zoneBox.currentTextChanged.connect(self.zoneBoxSelectionChanged)
        self.netBox.currentTextChanged.connect(self.netBoxSelectionChanged)
        self.tabView.clicked.connect(self.tableRowSelected_slot)
        ##self.tabView.currentChanged.connect(self.onSelectionChanged)

        mw.buttonM.clicked.connect(self.onMinus)
        mw.buttonP.clicked.connect(self.onPlus)
        mw.buttonReset.clicked.connect(self.onReset)
        mw.buttonOK.clicked.connect(self.onOK)

        for field in (mw.hostLineEdit, mw.nameAddressEdit, mw.ttlEdit, mw.typeEdit):
            field.textEdited.connect(self.onEdited)
        mw.rdataEdit.textChanged.connect(self.rdataEdited)

def zone_loaded(zone_name):
    """
    A new zone has been created"
    """
    global mw, edit_zone_view, zone_view_1, zone_view_2, zone_view_3

    if not edit_zone_view:
        edit_zone_view = ZoneEdit(mw.comboBoxMainZone,
                                  mw.comboBoxMainSub,
                                  mw.maintableView)
    if not zone_view_1:
        zone_view_1 = ZoneView(mw.comboBoxZone_1,
                               mw.comboBoxSub_1,
                               mw.tableView_1)
    if not zone_view_2:
        zone_view_2 = ZoneView(mw.comboBoxZone_2,
                               mw.comboBoxSub_2,
                               mw.tableView_2)
    if not zone_view_3:
        zone_view_3 = ZoneView(mw.comboBoxZone_3,
                               mw.comboBoxSub_3,
                               mw.tableView_3)
    
    z: zad.models.axfr.Zone = zad.models.axfr.Zone.zoneByName(zone_name)
    edit_zone_view.addZone(zone_name)
    if z.type == zad.common.ZTIP6:
        zone_view_3.addZone(zone_name)
    elif z.type == zad.common.ZTIP4:
        zone_view_2.addZone(zone_name)
    elif z.type == zad.common.ZTDOM:
        zone_view_1.addZone(zone_name)
