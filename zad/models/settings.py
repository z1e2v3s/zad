import logging
import sys
import time
import dns.query, dns.resolver, dns.zone, dns.rdataset, dns.rdatatype
import dns.exception
from PyQt5 import QtCore

import zad.common

l = logging.getLogger(__name__)




class SettingsModel(QtCore.QAbstractListModel):
    def __init__(self, data=[[]], parent=None):
        super().__init__(parent)

