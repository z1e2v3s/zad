import logging, sys

import ipaddress

import dns.rdata, dns.rdataclass, dns.rdataclass, dns.rdatatype
import dns.name, dns.resolver, dns.reversename, dns.exception

from PyQt5 import QtCore, QtWidgets

import zad.common
import zad.models.axfr
import zad.models.main
import zad.models.nsupdate

import zad.views.main

l = None

mw: 'zad.views.main.ZaMainWindow' = None

edit_zone_view = None
zone_view_1 = None
zone_view_2 = None
zone_view_3 = None


def setup(m_window):
    global mw
    mw = m_window


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
        self.zone: zad.models.axfr.Zone = None
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
            edit_zone_view.otherDoubleClicked(self, index)

    def addZone(self, zone_name):
        ct = cn = None
        if self.zoneBoxNames:
            ct = self.zoneBox.currentText()
        if zone_name in self.zoneBoxNames:
            self.zoneBoxNames.remove(zone_name)
            if self.zone.type != zad.common.ZTDOM:
                cn = self.net_name
        self.zoneBoxNames.append(zone_name)
        self.zoneBoxNames.sort()
        self.zoneBox.clear()
        self.zoneBox.addItems(self.zoneBoxNames)
        if ct:
            self.zoneBox.setCurrentText(ct)
        if cn:
            self.netBox.setCurrentText(cn)


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

    zoneEdit_message = QtCore.pyqtSignal(str)           # lmessages for status bar

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
        self.zone: zad.models.axfr.Zone = None
        self.zone_name = ''
        self.net_name = ''
        self.tableIndex: QtCore.QModelIndex = None
        
        self.formHost = ''
        self.formName = ''
        self.formttl = ''
        self.forType = ''
        self.formRdata = ''

        self.init_tabView()
        self.clearButtons()

        self.connect_signals()


    @QtCore.pyqtSlot(bool)
    def onMinus(self, checked):
        self.blockSignalsOfForm(True)
        ##self.tableIndex = None
        if zad.models.nsupdate.ddnsUpdate.delete(
            self.zone.name,
            mw.nameAddressEdit.text(),
            mw.typeEdit.text(),
            mw.rdataEdit.toPlainText(),
        ):
            zad.models.axfr.Zone.requestReload(self.zone.name)
        self.blockSignalsOfForm(False)
        self.clearButtons()
        self.clearForm()

    @QtCore.pyqtSlot(bool)
    def onPlus(self, checked):
        if not self.updateHost() or not self.formValid() or not mw.ttlEdit.text():
            zad.app.application.beep()
            return
        self.blockSignalsOfForm(True)
        if zad.models.nsupdate.ddnsUpdate.create(
            self.zone.name,
            mw.nameAddressEdit.text(),
            mw.ttlEdit.text(),
            mw.typeEdit.text(),
            mw.rdataEdit.toPlainText(),
        ):
            zad.models.axfr.Zone.requestReload(self.zone.name)
        self.blockSignalsOfForm(False)
        self.clearButtons()

    @QtCore.pyqtSlot(bool)
    def onReset(self, checked):
        self.reloadForm()

    @QtCore.pyqtSlot(bool)
    def onOK(self, checked):
        if not self.updateHost() or not self.formValid() or not mw.ttlEdit.text():
            zad.app.application.beep()
            return
        self.blockSignalsOfForm(True)
        ##self.tableIndex = None
        self.clearButtons()
        zad.models.nsupdate.ddnsUpdate.delete(
            self.zone.name,
            self.formName,
            self.formType,
            self.formRdata
        )
        zad.models.nsupdate.ddnsUpdate.create(
            self.zone.name,
            mw.nameAddressEdit.text(),
            mw.ttlEdit.text(),
            mw.typeEdit.text(),
            mw.rdataEdit.toPlainText(),
        )
        zad.models.axfr.Zone.requestReload(self.zone.name)

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
        mw.buttonP.setDefault(False)
        mw.buttonP.setDisabled(False)
        mw.buttonM.setDisabled(True)

    def formValid(self):
        name = mw.nameAddressEdit.text()
        try:
            n = dns.name.from_text(name)
            if not isinstance(n,  dns.name.Name):
                l.error('Editor: ?Malformed name {}'.format(name))
                self.zoneEdit_message.emit('?Malformed name {}'.format(name))
                return False
            z = str(dns.resolver.zone_for_name(name, tcp=True))
            if z != self.zone.name:
                l.error('?Editor: name not in current zone: {}'.format(name))
                self.zoneEdit_message.emit('?name not in current zone: {}'.format(name))
                return False
            rds = dns.rdataset.Rdataset(
                    dns.rdataclass.IN,
                    dns.rdatatype.from_text(mw.typeEdit.text())
                    )
            if mw.ttlEdit.text():
                rds.update_ttl(int(mw.ttlEdit.text()))
            rd = dns.rdata.from_text(
                            rds.rdclass,
                            rds.rdtype,
                            mw.rdataEdit.toPlainText())
            rds.add(rd)
        except BaseException:
            m = '?Editor: Bad RR: {} {} {}, \n because {} - {}'.format(name,
                                                                           mw.typeEdit.text(),
                                                                           mw.rdataEdit.toPlainText(),
                                                                           sys.exc_info()[0].__name__,
                                                                           str(sys.exc_info()[1]))
            l.error(m)
            self.zoneEdit_message.emit(m)
            return False
        return True

    def updateHost(self):
        if self.zone.type == zad.common.ZTDOM:
            return True
        af = mw.nameAddressEdit.text()
        hf = mw.hostLineEdit.text()
        if af == self.formName and hf == self.formHost:
            return True
        if hf != self.formHost:
            if not hf:                          # changing host to empty field is not allowed
                zad.app.application.beep()
                return False
            addr = self.addrFromHost(hf, self.zone.type, self.net_name)
            if addr:
                reverse_addr = addr.reverse_pointer + '.'
                mw.nameAddressEdit.setText(str(reverse_addr))
                return True
            else:
                return False
        else:
            if not af:                          # changing owner name to empty field is not allowed
                zad.app.application.beep()
                return False
            raddr = self.HostFromReverseAddr(af)
            if raddr:
                mw.hostLineEdit.setText(str(raddr))
                return True
            else:
                return False

    def addrFromHost(self, host, zone_type, net_name):
        """
        Return address as string from host
        """
        try:
            if zone_type == zad.common.ZTIP6:
                h = int(host, 16)
                net: ipaddress.IPv6Network = zad.models.axfr.ip6Nets[net_name]
                if h < 0 or h >= net.num_addresses:
                    raise ValueError('IPv6 Hostnumber out of range')
                else:
                    net_int = int(net.network_address)
                    addr_int = net_int + h
                    addr = ipaddress.IPv6Address(addr_int)
                    return addr
            else:
                h = int(host)
                net: ipaddress.IPv4Network = zad.models.axfr.ip4Nets[net_name]
                if h < 0 or h >= net.num_addresses:
                    raise ValueError('IPv4 Hostnumber out of range')
                else:
                    net_int = int(net.network_address)
                    addr_int = net_int + h
                    addr = ipaddress.IPv4Address(addr_int)
                    return addr
        except (TypeError, ValueError):
            m = '?Editor: Bad host number: "{}", \n because {} - {}'.format(host,
                                                                           sys.exc_info()[0].__name__,
                                                                           str(sys.exc_info()[1]))
            l.error(m)
            self.zoneEdit_message.emit(m)
            zad.app.application.beep()
            return ''
            

    def HostFromReverseAddr(self, reverse_addr):
        try:
            if self.zone.type == zad.common.ZTIP6:
                net = zad.models.axfr.ip6Nets[self.net_name]
                a = dns.reversename.to_address(dns.name.from_text(reverse_addr))
                addr = ipaddress.IPv6Address(a)
                if addr not in net:
                    zad.app.application.beep()
                    return ''
                host = int(addr) & int(net.hostmask)
                return hex(host)[2:]
            else:
                net = zad.models.axfr.ip4Nets[self.net_name]
                a = dns.reversename.to_address(dns.name.from_text(reverse_addr))
                addr = ipaddress.IPv4Address(a)
                if addr not in net:
                    zad.app.application.beep()
                    return ''
                host = int(addr) & int(net.hostmask)
            return host
        except dns.exception.DNSException:
            m = '?Editor: Bad origin IP: "{}", \n because {} - {}'.format(reverse_addr,
                                                                           sys.exc_info()[0].__name__,
                                                                           str(sys.exc_info()[1]))
            l.error(m)
            self.zoneEdit_message.emit(m)
            zad.app.application.beep()
            return ''


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
        self.loadBackup(index)
        self.reloadForm()

    def loadBackup(self, index):
        model = self.tabView.model()
        (self.formName, self.formTtl) = self.owner_name_ttl(model, index)
        if self.zone.type == zad.common.ZTDOM:
            self.formHost = ''
        else:
            i = model.createIndex(index.row(), 0)
            self.formHost = model.data(i, QtCore.Qt.DisplayRole)
        i = model.createIndex(index.row(), 3)
        self.formType = model.data(i, QtCore.Qt.DisplayRole)
        i = model.createIndex(index.row(), 4)
        self.formRdata = model.data(i, QtCore.Qt.DisplayRole)

    def reloadForm(self):
        mw.hostLineEdit.setText(self.formHost)
        mw.nameAddressEdit.setText(self.formName)
        mw.ttlEdit.setText(self.formTtl)
        mw.typeEdit.setText(self.formType)
        mw.rdataEdit.setText(self.formRdata)

        self.clearButtons()
        mw.buttonM.setDisabled(False)
        mw.buttonM.setDefault(True)
        self.blockSignalsOfForm(False)

    def owner_name_ttl(self, model, index) -> (str, str):
        """
        return owner name of RR by index
        """
        row = index.row()
        while row >= 0:
            i = model.createIndex(row, 1)
            name = model.data(i, QtCore.Qt.DisplayRole)
            i = model.createIndex(row, 2)
            ttl = model.data(i, QtCore.Qt.DisplayRole)

            if name:
                return (name, ttl)
            row -= 1
        return ('?','?')

    def clearForm(self):
        mw.hostLineEdit.clear()
        mw.nameAddressEdit.clear()
        mw.ttlEdit.clear()
        mw.typeEdit.clear()
        mw.rdataEdit.clear()

    def blockSignalsOfForm(self, state: bool):
        mw.hostLineEdit.blockSignals(state)
        mw.nameAddressEdit.blockSignals(state)
        mw.ttlEdit.blockSignals(state)
        mw.typeEdit.blockSignals(state)
        mw.rdataEdit.blockSignals(state)

    def clearButtons(self):
        mw.buttonM.setDisabled(True)
        mw.buttonM.setDefault(False)
        mw.buttonP.setDisabled(True)
        mw.buttonP.setDefault(False)
        mw.buttonOK.setDisabled(True)
        mw.buttonOK.setDefault(False)
        mw.buttonReset.setDisabled(True)
        mw.buttonReset.setDefault(False)

    def otherDoubleClicked(self, sender: ZoneView, index):
        other_zone: zad.models.axfr.Zone = zad.models.axfr.Zone.zoneByName(sender.zone.name)
        other_model = sender.tabView.model()
        i = other_model.index(index.row(), 0)
        other_host = other_model.data(i, QtCore.Qt.DisplayRole)

        i = other_model.index(index.row(), 1)
        other_type = other_model.data(i, QtCore.Qt.DisplayRole)

        own_type = mw.typeEdit.text()
        if own_type == 'A':
            if other_zone.type != zad.common.ZTIP4 or other_type != 'PTR':
                zad.app.application.beep()
                return
            other_addr = self.addrFromHost(other_host, other_zone.type, sender.net_name)
            if other_addr:
                mw.rdataEdit.setText(str(other_addr))
        elif own_type == 'AAAA':
            if other_zone.type != zad.common.ZTIP6 or other_type != 'PTR':
                zad.app.application.beep()
                return
            other_addr = self.addrFromHost(other_host, other_zone.type, sender.net_name)
            if other_addr:
                mw.rdataEdit.setText(str(other_addr))


    def selfSelected(self, zone_name, row):
        pass


    def addZone(self, zone_name):
        ct = cn = None
        if self.zoneBoxNames:
            ct = self.zoneBox.currentText()
        if zone_name in self.zoneBoxNames:
            self.zoneBoxNames.remove(zone_name)
            if self.zone.type != zad.common.ZTDOM:
                cn = self.net_name
        self.zoneBoxNames.append(zone_name)
        self.zoneBoxNames.sort()
        self.zoneBox.clear()
        self.zoneBox.addItems(self.zoneBoxNames)
        if ct:
            self.zoneBox.setCurrentText(ct)
        if cn:
            self.netBox.setCurrentText(cn)
        if self.tableIndex and self.tableIndex.isValid:
            self.tabView.selectRow(self.tableIndex.row())
            self.loadForm(self.tableIndex)
    
    def reload_table(self, zone_name):
        model = None
        if zone_name:
            self.zone: zad.models.axfr.Zone = zad.models.axfr.Zone.zoneByName(zone_name)
            if zone_name != self.zone_name:
                self.tableIndex = None
                self.zone_name = zone_name
        if self.zone.type in (zad.common.ZTIP4, zad.common.ZTIP6):                      # a net zone
            self.updateNets()
            if not self.net_name or self.net_name not in self.zone.nets.keys():
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
            if net_name != self.net_name:
                self.tableIndex = None
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
        mw.rdataEdit.acceptRichText = False
        mw.rdataEdit.textChanged.connect(self.rdataEdited)
        self.blockSignalsOfForm(True)


def zone_loaded(zone_name):
    """
    A new zone has been created"
    """
    global mw, l, edit_zone_view, zone_view_1, zone_view_2, zone_view_3

    if not edit_zone_view:
        edit_zone_view = ZoneEdit(mw.comboBoxMainZone,
                                  mw.comboBoxMainSub,
                                  mw.maintableView)
        edit_zone_view.zoneEdit_message.connect(mw.receive_status_bar_message)  ## FIXME
        l = logging.getLogger(__name__)                                         ## FIXME

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
