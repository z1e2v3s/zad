import logging
import sys
import time
import dns.query, dns.resolver, dns.zone, dns.rdataset, dns.rdatatype
import dns.exception

from PyQt5 import QtCore

import pyqtconfig

import zad.common

l = logging.getLogger(__name__)

conf: pyqtconfig.QSettingsManager = None




def setup():
    global conf
    
    QtCore.QCoreApplication.setOrganizationName("chaos1");
    QtCore.QCoreApplication.setOrganizationDomain("chaos1.de");
    QtCore.QCoreApplication.setApplicationName("zad");
    QtCore.QCoreApplication.setApplicationVersion(zad.get_version());

    conf = pyqtconfig.QSettingsManager()
    
    conf.set_defaults({
        "gen/master_server": '',                          # masterServerLineEdit
        "gen/ddns_key_file": '',                          # ddnsKeyFileLineEdit
        "gen/ns_for_axfr": zad.common.IP_XFR_NS,          # serverForZoneTransferLineEdit
        "gen/initial_domain": zad.common.INITIAL_DOMAIN,  # initialDomainLineEdit
        "gen/default_ip4_prefix": '24',                   # defaultPrefixIPv4LineEdit
        "gen/default_ip6_prefix": '64',                   # defaultPrefixIPv6LineEdit
        "gen/log_file": zad.common.DEFAULT_LOG_PATH,      # logfileLineEdit
        "gen/debug": False,                               # debugCheckBox
        "gen/ip4_nets": [],                               # iPv4ListWidget
        "gen/ip6_nets": [],                               # iPv6ListWidget
        "gen/ignored_nets": []                            # ignoredListWidget
    })