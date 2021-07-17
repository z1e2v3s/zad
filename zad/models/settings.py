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

        masterServer = None                         # masterServerLineEdit
        ddnsKeyFile = None                          # ddnsKeyFileLineEdit
        nsForAxfr = '2001:4bd8:0:104:217:17:192:66' # serverForZoneTransferLineEdit
        initialDomain = 'iks-jena.de'               # initialDomainLineEdit
        defaultIp4Prefix = 24                       # defaultPrefixIPv4LineEdit
        defaultIp6Prefix = 64                       # defaultPrefixIPv6LineEdit
        logFile = '/tmp/zad.log'                    # logfileLineEdit
        ip4Nets = []                                # iPv4ListWidget
        ip6Nets = []                                # iPv6ListWidget
        ignoredNets = []                            # ignoredListWidget




def setup():
    global settings
    QtCore.QCoreApplication.setOrganizationName("chaos1");
    QtCore.QCoreApplication.setOrganizationDomain("chaos1.de");
    QtCore.QCoreApplication.setApplicationName("zad");
    QtCore.QCoreApplication.setApplicationVersion(zad.get_version());

    settings = QtCore.QSettings()
