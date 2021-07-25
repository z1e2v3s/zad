import asyncio
import logging
import sys
import time

import dns.query, dns.resolver, dns.zone, dns.versioned, dns.rdataset, dns.rdatatype
import dns.exception
import dns.asyncquery, dns.asyncresolver

from PyQt5 import QtCore

from qasync import QEventLoop

import zad.common

l = logging.getLogger(__name__)

domainZones = {}
ip4Zones = {}
ip6Zones = {}

subdomains = {}
ip4Nets = {}
ip6Nets = {}


class RunThread(QtCore.QThread):
    axfr_message = QtCore.pyqtSignal(str)           # lmessages for status bar
    zone_loaded_message = QtCore.pyqtSignal(str)    # zone fqdn

    def __init__(self, loop: asyncio.AbstractEventLoop, parent=None):
        super(RunThread, self).__init__(parent)
        self.loop = loop
        self.coro_loadZones = loadZones
        # create 1st zone
        z = zad.common.INITIAL_DOMAIN
        if z[-1] != '.':
            z += '.'
        domainZones[z] = DomainZone(z)

    @QtCore.pyqtSlot(str)
    def set_text_slot(self, txt):
        self.text = txt

    def work(self):
        #run the event loop
        try:
            asyncio.ensure_future(self.coro_loadZones(self), loop=self.loop)
            ##await self.coro_loadZones
            self.loop.run_forever()

        finally:
            print("Disconnect...")

    def send_msg(self, name):
        self.axfr_message.emit(name)

    def send_zone_loaded(self, name):
        self.zone_loaded_message.emit(name)



async def do_axfr(ns, z):
    await dns.asyncquery.inbound_xfr(ns, z)

async def do_zoneName(fqdn):
    z = await dns.asyncresolver.zone_for_name(fqdn, tcp=True)
    return str(z)


class Zone(object):

    def zoneByName(zone_name):
        if zone_name.endswith('ip6.arpa.'):
            return ip6Zones[zone_name]
        elif zone_name.endswith('in-addr.arpa.'):
            return ip4Zones[zone_name]
        else:
            return domainZones[zone_name]
    
    
    def __init__(self, zone_name):
        global domainZones,ip4Zones,ip6Zones

        error = self.init_by_subclass   # bail out if not created as subclass
            
        
        self.zone_name = zone_name
        if self.zone_name[-1] != '.':
            self.zone_name += '.'
        self.zone_type: zad.common.ZoneTypes = None
        
        # add ourselves to globale zone list
        if self.zone_name.endswith('ip6.arpa.'):
            ip6Zones[self.zone_name] = self
        elif self.zone_name.endswith('in-addr.arpa.'):
            ip4Zones[self.zone_name] = self
        else:
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

    async def loadZone(self, runner: RunThread):
        row = 0
        self.z =  dns.zone.Zone(self.zone_name, relativize=False)

        runner.send_msg('Loading {} ...'.format(self.zone_name))

        for ns in [zad.common.IP_XFR_NS]:
            try:
                l.info('[Loading zone {} from NS {}]'.format(self.zone_name, ns))
                await do_axfr(ns, self.z)
                break
            except dns.xfr.TransferError:
                l.error('%loadZone: {} AXFR failed with NS={}'.format(self.zone_name, ns))
            except BaseException:
                l.error('%loadZone: {} Error on AXFR with NS={}'.format(self.zone_name, ns))
            
        else:
            l.error('?loadZone {} failed. Giving up.'.format(self.zone_name))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.zone_name))
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
                        await self.createZoneFromName(srdatatype, srdata)
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
        runner.send_msg('Loading of {} completed with {} RRs'.format(self.zone_name, row -2))
        runner.send_zone_loaded(self.zone_name)

    async def createZoneFromName(self, dtype, name):
        global domainZones, ip4Zones, ip6Zones

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
            zoneName = await do_zoneName(fqdn)
            l.debug('createZoneFromName: name={}, fqdn={} OK: zone={}'.format(name, fqdn, zoneName))
        except dns.name.EmptyLabel:
            l.warning('%Empty label: name={}, dtype={}'.format(name, dtype))
            return
        except dns.exception.Timeout:
            l.warning('%{} timed out . . .'.format(fqdn))
            for i in range(zad.common.TIMEOUT_RETRIES):
                time.sleep(zad.common.TIMEOUT_SLEEP)
                try:
                    zoneName = await do_zoneName(fqdn)
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


class DomainZone(Zone):
    def __init__(self, zone_name):
        self.init_by_subclass = True
        self.type = zad.common.ZTDOM
        super(DomainZone, self).__init__(zone_name)


class Ip4Zone(Zone):
    def __init__(self, zone_name):
        self.init_by_subclass = True
        self.type = zad.common.ZTIP4
        super(Ip4Zone,self).__init__(zone_name)

class Ip6Zone(Zone):
    def __init__(self, zone_name):
        self.init_by_subclass = True
        self.type = zad.common.ZTIP6
        super(Ip6Zone,self).__init__(zone_name)


async def loadZones(runner: RunThread):
    """
    Check for zones which not have been loaded and load them
    """
    def find_next_zone():
        zone_list = []
        for d in (domainZones, ip4Zones, ip6Zones):
            for k in d.keys():
                z = d[k]
                if len(z.d) < 2:
                    zone_list.append((z))
        if zone_list:
            return zone_list[0]
        else:
            return None

    while True:
        z = find_next_zone()
        if z:
            await z.loadZone(runner)
            await asyncio.sleep(5)
        else:
            runner.send_msg('All zones loaded.')
            break

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
