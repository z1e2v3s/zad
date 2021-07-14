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
    def __init__(self, data=[[]], parent=None):
        super(ZoneModel, self).__init__(parent)
        self.vrrs: [[str,str,str]] = data

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return ['OwnerName', 'Type', 'Rdata'][section]
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
            if column > 0:
                column += 1
            v = self.vrrs[row][column]
            if not v:
                v = ''
            return str(v)


class EditZoneModel(ZoneModel):
    def __init__(self, data=[[]], parent=None):
        super(EditZoneModel, self).__init__(parent)
        self.vrrs: [[str,str,str,str]] = data

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return ['OwnerName', 'TTL', 'Type', 'Rdata'][section]
            else:
                return None

    def columnCount(self, parent=None):
        return 4

    def data(self, index: QtCore.QModelIndex, role: int):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            v = self.vrrs[row][column]
            if not v:
                v = ''
            return str(v)
