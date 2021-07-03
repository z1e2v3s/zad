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
        super().__init__(parent)
        self.zone = Zone(zad.common.INITIAL_DOMAIN)     # hack

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
        
        # add ourselves to globale zone list
        if self.zone_name.endswith('ip6.arpa.'):
            if self.zone_name not in ip6Zones:
                ip6Zones[self.zone_name] = self
        elif self.zone_name.endswith('in-addr.arpa.'):
            if self.zone_name not in ip4Zones:
                ip4Zones[self.zone_name] = self
        else:
            if self.zone_name not in domainZones:
                domainZones[self.zone_name] = self
            
        self.z = None
        self.d = [['', '', '', '']]
        self.valid = False

    def data(self, row: int, column: int) -> str:
        if not self.z:
            self.loadZone()          
        v = self.d[row][column]
        if not v: v = ''
        return str(v)

    async def do_axfr(self):
        self.z = dns.asyncquery.inbound_xfr(ns, self.z)

    async def loadZone(self):
        row = 0
        self.z =  dns.zone.Zone(self.zone_name, relativize=False)
        for ns in zad.common.IP_XFR_NS:
            try:
                l.info('[Loading zone {} from NS {}]'.format(self.zone_name, ns))
                await self.do_axfr()
                break
            except dns.xfr.TransferError:
                l.error('%loadZone: {} AXFR failed with NS={}'.format(self.zone_name, ns))
            except BaseException:
                l.error('%loadZone: {} Error on AXFR with NS={}'.format(self.zone_name, ns))
            
        else:
            l.error('?loadZone {} failed. Giving up.'.format(self.zone_name))
            self.d = [['', '', '', ''], ['', '', '', '']]
            return
        
        l.debug('[loadZone: zone={}, AXFR of {} nodes done'.format(self.zone_name, len(self.z.keys())))
        for k in self.z.keys():
            zn = name = str(k)
            if name == '@': name = ''
            self.d[row][0] = name
            node = self.z[zn]
            for the_rdataset in node:
                self.d[row][1] = str(the_rdataset.ttl)
                for rdata in the_rdataset:
                    srdatatype = dns.rdatatype.to_text(the_rdataset.rdtype)
                    if srdatatype not in ('RRSIG', 'NSEC', 'NSEC3'):
                        self.d[row][2] = srdatatype
                        srdata = str(rdata)
                        self.d[row][3] = srdata
                        if srdatatype == 'MX':
                            srdata = str(rdata.exchange)
                        self.createZoneFromName(srdatatype, srdata)
                        row = row + 1
                        self.d.append(['', '', '', ''])
                    ##l.debug('.', end=' ', flush=True)
                ##l.debug('+', end=' ', flush=True)
        self.valid = True
        l.info('[loadZone: {} RRs out of {} nodes from zone {} loaded.]'.format(
                                                            row -2,
                                                            len(self.z.keys()),
                                                            self.zone_name))
        logZones()
        
    async def do_zoneName(fqdn):
        return str(dns.asyncresolver.zone_for_name(fqdn, tcp=True))

    async def createZoneFromName(self, dtype, name):

        if dtype in ('NS', 'MX', 'CNAME', 'DNAME', 'PTR', 'SRV'):   # a domain fqdn
            if name[-1] == '.':  # already absolute?
                fqdn = name
            else:               # no, relative - make absolute
                fqdn = name + '.' + self.zone_name
            if len(domainZones.keys()) > zad.common.MAX_ZONES:
                return
        elif dtype == 'A':                                # address
            if len(ip4Zones.keys()) > zad.common.MAX_ZONES:
                return
            fqdn = dns.reversename.from_address(name)
        elif dtype == 'AAAA':                                # address
            if len(ip6Zones.keys()) > zad.common.MAX_ZONES:
                return
            fqdn = dns.reversename.from_address(name)
        else:                                                       # ignore others
            return
        try:
            zoneName = await self.do_zoneName(fqdn)
            l.debug('createZoneFromName: name={}, fqdn={} OK: zone={}'.format(name, fqdn, zoneName))
        except dns.name.EmptyLabel:
            l.warning('%Empty label: name={}, dtype={}'.format(name, dtype))
            return
        except dns.exception.Timeout:
            l.warning('%{} timed out . . .'.format(fqdn))
            for i in range(zad.common.TIMEOUT_RETRIES):
                time.sleep(zad.common.TIMEOUT_SLEEP)
                try:
                    zoneName = await self.do_zoneName(fqdn)
                except dns.name.EmptyLabel:
                    l.warning('%Empty label: name={}, dtype={}'.format(name, dtype))
                    return
                except dns.exception.Timeout:
                    l.warning('%{} timed out . . .'.format(fqdn))
                    continue
                except BaseException:
                    l.error('%createZoneFromName/zone_for_name name={}, fqdn={},\n    because {} [{}]'.
                         format(name, fqdn,
                         sys.exc_info()[0].__name__,
                         str(sys.exc_info()[1])))
                    return
            else:
                return
        except BaseException:
            l.error('%createZoneFromName/zone_for_name name={}, fqdn={},\n    because {} [{}]'.
                 format(name, fqdn,
                 sys.exc_info()[0].__name__,
                 str(sys.exc_info()[1])))
            return
        ##l.debug('type={}, name={}, fqdn={}, zone={}'.format(dtype, name, fqdn, zoneName))
        l.debug('createZoneFromName: {}'.format(fqdn))
        if dtype == 'A' and zoneName not in ip4Zones:
            ip4Zones[zoneName] = Ip4Zone(zoneName)
        elif dtype == 'AAAA' and zoneName not in ip6Zones:
            ip6Zones[zoneName] = Ip6Zone(zoneName)
        elif dtype in ('NS', 'MX', 'CNAME', 'DNAME', 'PTR', 'SRV') and zoneName not in domainZones:
            domainZones[zoneName] = DomainZone(zoneName)
        if zad.common.DEBUG: print('createZoneFromName: {} done'.format(fqdn))

    def columnCount(self):
        if not self.z :
            self.loadZone()
        return 4

    def rowCount(self):
        if not self.z:
            self.loadZone()
        return len(self.d) -1       # why -1 ?

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


def logZones():
    l.info('[Known Zones:]')
    pd = ''
    i = 0
    dtn = ['Domain Zones', 'IP4 Zones', 'IP6 Zones']
    
    for d in (domainZones, ip4Zones, ip6Zones):
        if not pd == d:
            l.info('\n[{}]'.format(dtn[i]))
            pd = d
            i += 1
        for k in d.keys():
            z = d[k]
            l.info('{}{}'.format(k, '[loaded]' if len(z.d) > 1 else ''))

def setupResolver(resolver_addresses):

    if not resolver_addresses:
        return
    
    dns.resolver.get_default_resolver()
    dns.resolver.default_resolver.nameservers = resolver_addresses
    dns.resolver.default_resolver.cache = dns.resolver.LRUCache()


def setup():
    setupResolver(zad.common.IP_RESOLVER)
