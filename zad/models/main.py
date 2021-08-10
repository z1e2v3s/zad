import logging
import sys
import time
import dns.query, dns.resolver, dns.zone, dns.versioned, dns.rdataset, dns.rdatatype
import dns.exception
import dns.asyncbackend, dns.asyncquery
from PyQt5 import QtCore

import zad.common

l = logging.getLogger(__name__)
dns.asyncbackend.set_default_backend('asyncio')

domainZones = {}
ip4Zones = {}
ip6Zones = {}

subdomains = {}
ip4Nets = {}
ip6Nets = {}


class ZoneModel(QtCore.QAbstractTableModel):

    def __init__(self, data=[[]], netZone=False, parent=None):
        super(ZoneModel, self).__init__(parent)
        self.vrrs = data
        self.netZone = netZone

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                f1 = 'Host' if self.netZone else 'OwnerName'
                return [f1, 'Type', 'Rdata'][section]
            else:
                return None

    def columnCount(self, parent=None):
        return 3

    def rowCount(self, parent=None):
        return len(self.vrrs) -1

    def data(self, index: QtCore.QModelIndex, role: int):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if self.netZone:
                if column > 0:
                    column += 2
            else:
                column += 1
                if column > 1:
                    column += 1
            v = self.vrrs[row][column]
            if not v:
                v = ''
            return str(v)

class EditZoneModel(ZoneModel):
    def __init__(self, data=[[]], netZone=False, parent=None):
        super(EditZoneModel, self).__init__(parent)
        self.vrrs = data
        self.netZone = netZone

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return ['Host', 'OwnerName', 'TTL', 'Type', 'Rdata'][section]
            else:
                return None

    def columnCount(self, parent=None):
        return 5

    def data(self, index: QtCore.QModelIndex, role: int):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            v = self.vrrs[row][column]
            if not v:
                v = ''
            return str(v)

    """
    # keep column width with header
    def columnWidth(self) -> list(tuple):
        l = []
        if self netZone:
            l.append(0,20)
            l.append(1,100)
            l.append(2,10)
            l.append(3,10)
            l.append(4,400)
        else:
            l.append(0,120)
            l.append(1,10)
            l.append(2,10)
            l.append(3,400)
        return l
    """