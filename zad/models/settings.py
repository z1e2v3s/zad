import logging

from PyQt5 import QtCore

import zad.common

l = logging.getLogger(__name__)

settings: QtCore.QSettings = None


def setup():
    global settings

    QtCore.QCoreApplication.setOrganizationName("chaos1")
    QtCore.QCoreApplication.setOrganizationDomain("chaos1.de")
    QtCore.QCoreApplication.setApplicationName("zad")
    QtCore.QCoreApplication.setApplicationVersion(zad.get_version())

    settings = QtCore.QSettings()

    if not (settings.contains('gen/ns_for_axfr') and
            settings.contains('gen/initial_domain') and
            settings.contains('gen/default_ip4_prefix') and
            settings.contains('gen/default_ip6_prefix') and
            settings.contains('gen/log_file')):

        settings.setValue('gen/master_server', '')                           # masterServerLineEdit
        settings.setValue("gen/ddns_key_file", '')                          # ddnsKeyFileLineEdit
        settings.setValue("gen/ns_for_axfr", zad.common.IP_XFR_NS)          # serverForZoneTransferLineEdit
        settings.setValue("gen/initial_domain", zad.common.INITIAL_DOMAIN)  # initialDomainLineEdit
        settings.setValue("gen/default_ip4_prefix", 24)                     # defaultPrefixIPv4LineEdit
        settings.setValue("gen/default_ip6_prefix", 64)                     # defaultPrefixIPv6LineEdit
        settings.setValue("gen/log_file", zad.common.DEFAULT_LOG_PATH)      # logfileLineEdit
        settings.setValue("gen/debug", False)                               # debugCheckBox

    return settings

def getNetList(name) -> []:
    global settings

    li = []
    ##if settings.contains(name):

    size: int = settings.beginReadArray(name)
    print('get:size ' + str(size))
    for i in range(size):
        settings.setArrayIndex(i)
        li.append(settings.value('net'))
    settings.endArray()

    print('get: result ' + repr(li))
    return li


def updateNetList(name: str, theList: []):
    global settings
    print('update ' + repr(theList))
    if settings.contains(name):
        print('update: Removing all')
        settings.remove(name)
    theList.sort()
    settings.beginWriteArray(name)
    for i in range(len(theList)):
        settings.setArrayIndex(i)
        settings.setValue('net', theList[i])
        print('update: Setting {}'.format(theList[i]))
    settings.endArray()