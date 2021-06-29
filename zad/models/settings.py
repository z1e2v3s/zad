import logging
import sys
import time
import dns.query, dns.resolver, dns.zone, dns.rdataset, dns.rdatatype
import dns.exception
from PyQt5 import QtCore

import zad.common

l = logging.getLogger(__name__)

settings: QtCore.QSettings = None


class SettingsModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)


def setup():
    QtCore.QCoreApplication.setOrganizationName("chaos1.de");
    QtCore.QCoreApplication.setApplicationName("zad");
    QtCore.QCoreApplication.setApplicationVersion(zad.get_version());

    settings = QtCore.QSettings()
