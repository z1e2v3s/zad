import logging
from PyQt5 import QtCore, QtWidgets

import zad.models.axfr
import zad.models.main
import zad.views.main

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
        self.init_tabView()
        self.connect_signals()

    @QtCore.pyqtSlot(str)
    def zoneBoxSelectionChanged(self, zone_name: str):
        if zone_name:
            self.reload_table(zone_name)

    def addZone(self, zone_name):
        self.zoneBoxNames.append(zone_name)
        self.zoneBoxNames.sort()
        ct = None
        if self.zoneBoxNames:
            ct = self.zoneBox.currentText()
        self.zoneBox.clear()
        self.zoneBox.addItems(self.zoneBoxNames)
        if ct:
            self.zoneBox.setCurrentText(ct)

    def reload_table(self, zone_name):
        zone = zad.models.axfr.Zone.zoneByName(zone_name)
        model = zad.models.main.ZoneModel(zone.d)
        self.tabView.setModel(model)
        self.zoneBox.setCurrentText(zone_name)

    def init_tabView(self):
        self.tabView.setColumnWidth(0, 100)
        self.tabView.setColumnWidth(1, 40)
        self.tabView.setColumnWidth(2, 100)
        hh = self.tabView.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def connect_signals(self):
        self.zoneBox.currentTextChanged.connect(self.zoneBoxSelectionChanged)



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
        self.init_tabView()
        self.connect_signals()

    def reload_table(self, zone_name):
        zone = zad.models.axfr.Zone.zoneByName(zone_name)
        model = zad.models.main.EditZoneModel(zone.d)
        self.tabView.setModel(model)
        self.zoneBox.setCurrentText(zone_name)

    def init_tabView(self):
        self.tabView.setColumnWidth(0, 100)
        self.tabView.setColumnWidth(1, 40)
        self.tabView.setColumnWidth(2, 40)
        self.tabView.setColumnWidth(3, 400)
        hh = self.tabView.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)





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
    
    edit_zone_view.addZone(zone_name)
    z: zad.models.axfr.Zone = zad.models.axfr.Zone.zoneByName(zone_name)
    if zone_name.endswith('ip6.arpa.'):
        zone_view_3.addZone(zone_name)
    elif zone_name.endswith('in-addr.arpa.'):
        zone_view_2.addZone(zone_name)
    else: zone_view_1.addZone(zone_name)
