import logging
from PyQt5 import QtCore, QtWidgets

import zad.models.axfr
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
                 table: QtWidgets.QTableView,
                 parent=None):
        super(ZoneView, self).__init__(parent)

        self.zoneBox: QtWidgets.QComboBox = zoneBox
        ##self.zoneBox.insertPolicy = QtWidgets.QComboBox.InsertPolicy.InsertAlphabetically
        self.netBox: QtWidgets.QComboBox = netBox
        ##self.netBox.insertPolicy = QtWidgets.QComboBox.InsertPolicy.InsertAlphabetically
        self.table = table
        self.zoneBoxNames = []
        self.netBoxNames = []
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
            i = self.zoneBox.findData(ct)
            self.zoneBox.setCurrentIndex(i)

    def reload_table(self, zone_name):
        pass

    def connect_signals(self):
        self.zoneBox.currentTextChanged.connect(self.zoneBoxSelectionChanged)



class ZoneEdit(ZoneView):
    pass





def zone_loaded(zone_name):
    """
    A new zone has been created"
    """
    global mw, edit_zone_view, zone_view_1, zone_view_2, zone_view_3

    zone: zad.models.axfr.Zone = None
    if zone_name.endswith('ip6.arpa.'):
        zone = zad.models.axfr.ip6Zones[zone_name]
    elif zone_name.endswith('in-addr.arpa.'):
        zone = zad.models.axfr.ip4Zones[zone_name]
    else: zone = zad.models.axfr.domainZones[zone_name]
   
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
    
    for v in (edit_zone_view, zone_view_1, zone_view_2, zone_view_3):
        v.addZone(zone_name)

    
