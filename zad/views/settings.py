import logging
from PyQt5 import QtWidgets, QtCore
import pyqtconfig

import zad.pyuic.settings
import zad.models.main
import zad.models.settings


class ZaSettinsDialog(QtWidgets.QDialog,zad.pyuic.settings.Ui_settingsTabWidget):
    def __init__(self):
        super(ZaSettinsDialog,self).__init__()
        self.setupUi(self)

sd: ZaSettinsDialog = None
l = logging.getLogger(__name__)

@QtCore.pyqtSlot()
def showSettings():
    global sd
    sd.show()

def setup():
    global settingsDialog, sd

    sc: pyqtconfig.QSettingsManager = zad.models.settings.conf
    sd = ZaSettinsDialog()

    sc.add_handler("gen/master_server", sd.masterServerLineEdit)
    sc.add_handler("gen/ddns_key_file", sd.ddnsKeyFileLineEdit)
    sc.add_handler("gen/ns_for_axfr", sd.serverForZoneTransferLineEdit)
    sc.add_handler("gen/initial_domain", sd.initialDomainLineEdit)
    sc.add_handler("gen/default_ip4_prefix", sd.defaultPrefixIPv4LineEdit)
    sc.add_handler("gen/default_ip6_prefix", sd.defaultPrefixIPv6LineEdit)
    sc.add_handler("gen/log_file", sd.logfileLineEdit)
    sc.add_handler("gen/debug", sd.debugCheckBox)
    sc.add_handler("gen/ip4_nets", sd.iPv4ListWidget)
    sc.add_handler("gen/ip6_nets", sd.iPv6ListWidget)
    sc.add_handler("gen/ignored_nets", sd.ignoredListWidget)
