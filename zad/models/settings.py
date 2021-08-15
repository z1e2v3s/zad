import logging

from PyQt5 import QtCore

import zad.common

l = logging.getLogger(__name__)

class Prefs(QtCore.QObject):
    """
    storage manager for settings
    """
    def __init__(self):

        super(Prefs, self).__init__()

        QtCore.QCoreApplication.setOrganizationName("chaos1")
        QtCore.QCoreApplication.setOrganizationDomain("chaos1.de")
        QtCore.QCoreApplication.setApplicationName("zad")
        QtCore.QCoreApplication.setApplicationVersion(zad.get_version())

        self._settings = QtCore.QSettings()

        self._master_server = ''
        self._ddns_key_file = ''
        self._ns_for_axfr = ''
        self._initial_domain = ''
        self._default_ip4_prefix = None
        self._default_ip6_prefix = None
        self._log_file = ''
        self._debug = False
        self._ip4_nets = []
        self._ip6_nets = []
        self._ignored_zones = []

        self._settings.beginGroup('gen')
        keys = self._settings.childKeys()
        self._settings.endGroup()
        if len(keys) < 8:               # do we have something on fallback?
                                        # no - initialize with default values and create fallback
            self._settings.setValue('gen/master_server', '')  # masterServerLineEdit
            self._settings.setValue("gen/ddns_key_file", '')  # ddnsKeyFileLineEdit
            self._settings.setValue("gen/ns_for_axfr", zad.common.IP_XFR_NS)  # serverForZoneTransferLineEdit
            self._settings.setValue("gen/initial_domain", zad.common.INITIAL_DOMAIN)  # initialDomainLineEdit
            self._settings.setValue("gen/default_ip4_prefix", '24')  # defaultPrefixIPv4LineEdit
            self._settings.setValue("gen/default_ip6_prefix", '64')  # defaultPrefixIPv6LineEdit
            self._settings.setValue("gen/log_file", zad.common.DEFAULT_LOG_PATH)  # logfileLineEdit
            self._settings.setValue("gen/debug", 'False')  # debugCheckBox

            self._settings.sync()

        self._read_all_settings()       # sync our vars with fallback

    @property
    def master_server(self):
            return self._master_server
            
    @master_server.setter
    def master_server(self, master_server):
        self._master_server = master_server
        self._settings.setValue('gen/master_server', master_server)
    
    
    @property
    def ddns_key_file(self):
            return self._ddns_key_file
            
    @ddns_key_file.setter
    def ddns_key_file(self, ddns_key_file):
        self._ddns_key_file = ddns_key_file
        self._settings.setValue('gen/ddns_key_file', ddns_key_file)

    
    @property
    def ns_for_axfr(self):
            return self._ns_for_axfr
            
    @ns_for_axfr.setter
    def ns_for_axfr(self, ns_for_axfr):
        self._ns_for_axfr = ns_for_axfr
        self._settings.setValue('gen/ns_for_axfr', ns_for_axfr)

    
    @property
    def initial_domain(self):
            return self._initial_domain
            
    @initial_domain.setter
    def initial_domain(self, initial_domain):
        self._initial_domain = initial_domain
        self._settings.setValue('gen/initial_domain', initial_domain)

    
    @property
    def default_ip4_prefix(self):
            return self._default_ip4_prefix
            
    @default_ip4_prefix.setter
    def default_ip4_prefix(self, default_ip4_prefix):
        self._default_ip4_prefix = default_ip4_prefix
        self._settings.setValue('gen/default_ip4_prefix', str(default_ip4_prefix))

    
    @property
    def default_ip6_prefix(self):
            return self._default_ip6_prefix
            
    @default_ip6_prefix.setter
    def default_ip6_prefix(self, default_ip6_prefix):
        self._default_ip6_prefix = default_ip6_prefix
        self._settings.setValue('gen/default_ip6_prefix', str(default_ip6_prefix))

    
    @property
    def log_file(self):
            return self._log_file
            
    @log_file.setter
    def log_file(self, log_file):
        self._log_file = log_file
        self._settings.setValue('gen/log_file', log_file)

    
    @property
    def debug(self):
            return self._debug
            
    @debug.setter
    def debug(self, debug):
        self._debug = debug
        self._settings.setValue('gen/debug', str(debug))

    
    @property
    def ip4_nets(self):
            return self._ip4_nets
    
    @property
    def ip6_nets(self):
            return self._ip6_nets

    @property
    def ignored_zones(self):
            return self._ignored_zones
            

    def sync(self):
        self._settings.sync()

    def get_net_list(self, name) -> []:
    
        li = []
    
        size: int = self._settings.beginReadArray(name)
        ## print('get:size ' + str(size))
        for i in range(size):
            self._settings.setArrayIndex(i)
            li.append(self._settings.value('net'))
        self._settings.endArray()
    
        setattr(self, '_' + name, li)
        return li
    
    
    def _updateNetList(self, name: str, theList: []):

        ## print('update ' + repr(theList))
        if self._settings.contains(name):
            ## print('update: Removing all')
            self._settings.remove(name)
        theList.sort()
        self._settings.beginWriteArray(name)
        for i in range(len(theList)):
            self._settings.setArrayIndex(i)
            self._settings.setValue('net', theList[i])
            ## print('update: Setting {}'.format(theList[i]))
        self._settings.endArray()
        setattr(self, '_' + name, theList)


    def _read_all_settings(self):
    
        self._master_server = self._settings.value('gen/master_server') 
        self._ddns_key_file = self._settings.value("gen/ddns_key_file")
        self._ns_for_axfr = self._settings.value("gen/ns_for_axfr")
        self._initial_domain = self._settings.value("gen/initial_domain")
        self._default_ip4_prefix = int(self._settings.value("gen/default_ip4_prefix"))
        self._default_ip6_prefix = int(self._settings.value("gen/default_ip6_prefix"))
        self._log_file = self._settings.value("gen/log_file")
        self._debug = self._settings.value("gen/debug").lower() in ('true', 'yes', '1', 't', 'y')

        for name in ('ip4_nets', 'ip6_nets', 'ignored_zones'):
            lst = self.get_net_list(name)
            setattr(self, '_' + name, lst)

