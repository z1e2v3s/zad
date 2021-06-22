from PyQt5 import QtCore

import dns.query, dns.resolver, dns.zone, dns.rdataset, dns.rdatatype
import sys

import zad.common

domainZones = {}
ip4Zones = {}
ip6Zones = {}

subdomains = {}
ip4Nets = {}
ip6Nets = {}



class ZoneModel(QtCore.QAbstractTableModel):
    def __init__(self, data=[[]], parent=None):
        super().__init__(parent)
        self.zone = Zone('iks-jena.de')

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return ['OwnerName', 'TTL', 'Type', 'Rdata'][section]
            else:
                return None

    def columnCount(self, parent=None):
        return self.zone.columnCount()

    def rowCount(self, parent=None):
        return self.zone.rowCount()

    def data(self, index: QtCore.QModelIndex, role: int):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return self.zone.data(row, col)


class Zone(object):

    def __init__(self, zone_name):
        self.zone_name = zone_name
        if self.zone_name[-1] != '.':
            self.zone_name += '.'
        self.z = dns.zone
        self.d = [['', '', '', '']]
        self.valid = False

    def data(self, row: int, column: int) -> str:
        if not self.d:
            self.loadZone()          
        v = self.d[row][column]
        if not v: v = ''
        return str(v)

    def loadZone(self):
        row = 0

        print('[loadZone: zone={}, NS={}]'.format(self.zone_name, zad.common.IP_XFR_NS))
        for ns in zad.common.IP_XFR_NS:
            try:
                self.z = dns.zone.from_xfr(dns.query.xfr(ns, self.zone_name))
                break
            except dns.xfr.TransferError:
                print('%loadZone: AXFR failed with NS={}'.format(ns))
            except BaseException:
                print('%loadZone: Error on AXFR with NS={}'.format(ns))
            
        else:
            print('?loadZone failed. Giving up.')
            self.d = [['', '', '', ''], ['', '', '', '']]
            return
        
        print('[loadZone: zone={}, loaded with {} RRs'.format(self.zone_name, len(self.z.keys())))
        for name in self.z.keys():
            zn = name = str(name)
            if name == '@': name = ''
            self.d[row][0] = name
            node = self.z[zn]
            for the_rdataset in node:
                self.d[row][1] = str(the_rdataset.ttl)
                for rdata in the_rdataset:
                    srdatatype = dns.rdatatype.to_text(the_rdataset.rdtype)
                    self.d[row][2] = srdatatype
                    srdata = str(rdata)
                    self.d[row][3] = srdata
                    if srdatatype == 'MX':
                        srdata = str(rdata.exchange)
                    self.createZoneFromName(srdatatype, srdata)
                    row = row + 1
                    self.d.append(['', '', '', ''])
        self.valid = True
        print('[loadZone: zone={} done.]'.format(self.zone_name))
        

    def createZoneFromName(self, dtype, name):

        if dtype in ('NS', 'MX', 'CNAME', 'DNAME', 'PTR', 'SRV'):   # a domain fqdn
            if name[-1] == '.':  # already absolute?
                fqdn = name
            else:               # no, relative - make absolute
                fqdn = name + '.' + self.zone_name
        elif dtype in ('A', 'AAAA'):                                # address
            fqdn = dns.reversename.from_address(name)
        else:                                                       # ignore others
            return
        try:
            print('createZoneFromName: {}'.format(fqdn))
            zoneName = str(dns.resolver.zone_for_name(fqdn))
            print('createZoneFromName: {} done'.format(fqdn))
        except dns.name.EmptyLabel:
            print('Empty label: name={}, dtype={}'.format(name, dtype))
        except BaseException:
            return
        ##print('type={}, name={}, fqdn={}, zone={}'.format(dtype, name, fqdn, zoneName))
        if dtype == 'A' and zoneName not in ip4Zones:
            ip4Zones[zoneName] = Ip4Zone(zoneName)
        elif dtype == 'AAAA' and zoneName not in ip6Zones:
            ip6Zones[zoneName] = Ip6Zone(zoneName)
        elif dtype in ('NS', 'MX', 'CNAME', 'DNAME', 'PTR', 'SRV') and zoneName not in domainZones:
            domainZones[zoneName] = DomainZone(zoneName)

    def columnCount(self):
        if len(self.d) < 2:
            self.loadZone()
        return len(self.d[0])

    def rowCount(self):
        if len(self.d) < 2:
            self.loadZone()
        return len(self.d)

class DomainZone(Zone):
    def __init__(self, zone_name):
        super(DomainZone,self).__init__(zone_name)

class Ip4Zone(Zone):
    def __init__(self, zone_name):
        super(Ip4Zone,self).__init__(zone_name)

class Ip6Zone(Zone):
    def __init__(self, zone_name):
        super(Ip6Zone,self).__init__(zone_name)



def loadZones():
    """
    Check for zones which not have been loaded and load them
    """
    zone_list = []
    for d in (domainZones, ip4Zones, ip6Zones):
        for k in d.keys():
            z = d[k]
            if len(z.d) < 2:
                zone_list.append(z)
    for z in zone_list:
        z.loadZone()


def setupResolver(resolver_addresses):

    dns.resolver.get_default_resolver()
    dns.resolver.default_resolver.nameservers = resolver_addresses
    dns.resolver.default_resolver.cache = dns.resolver.LRUCache()


def setup():
    setupResolver(zad.common.IP_RESOLVER)
