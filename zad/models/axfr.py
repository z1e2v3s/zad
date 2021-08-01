import asyncio
import ipaddress
import logging
import re
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
        z = zad.prefs.initial_domain
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
        self.d = [['', '', '', '', '', '']] # name, ttl, type, rdata, host, net
        self.valid = False

        self.getNetsFromPrefs()
        
        self.nets = {}

        if self.zone_name.endswith('ip6.arpa.'):
            self.default_net_mask = int(ipaddress.IPv6Network('1::/{}'.format(
                                                zad.prefs.default_ip6_prefix)).netmask)
            self.default_host_mask = int(ipaddress.IPv6Network('1::/{}'.format(
                                                zad.prefs.default_ip6_prefix)).hostmask)
        else:
            self.default_net_mask = int(ipaddress.IPv4Network('1.0.0.0/{}'.format(
                                                zad.prefs.default_ip4_prefix)).netmask)
            self.default_host_mask = int(ipaddress.IPv4Network('1.0.0.0/{}'.format(
                                                zad.prefs.default_ip4_prefix)).hostmask)


    def data(self, row: int, column: int) -> str:
        if not self.z:
            self.loadZone()          
        v = self.d[row][column]
        if not v: v = ''
        return str(v)

    async def loadZone(self, runner: RunThread):
        """
        Inherited by Ip4Zone and Ip6Zone
        """
        row = 0
        self.z = dns.zone.Zone(self.zone_name, relativize=False)
        runner.send_msg('Loading {} ...'.format(self.zone_name))
        ns = zad.prefs.ns_for_axfr
        ok = False

        try:
            l.info('[Loading zone {} from NS {}]'.format(self.zone_name, ns))
            await do_axfr(ns, self.z)
            ok = True
        except dns.xfr.TransferError:
            l.error('?loadZone: {} AXFR failed with NS={}'.format(self.zone_name, ns))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.zone_name))
        except BaseException:
            l.error('%loadZone: {} Error on AXFR with NS={}, \n because {} - {}'.format(self.zone_name,
                                                                                        ns,
                                                                                        sys.exc_info()[0].__name__,
                                                                                        str(sys.exc_info()[1])))
            runner.send_msg('%loadZone: {} Error on AXFR with NS={}, because {} - {}'.format(self.zone_name,
                                                                                        ns,
                                                                                        sys.exc_info()[0].__name__,
                                                                                        str(sys.exc_info()[1])))

        if not ok:
            l.error('?loadZone {} failed. Giving up.'.format(self.zone_name))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.zone_name))
            self.d = [['', '', '', '', '', ''], ['', '', '', '', '', '']]
            return

        err = ''
        try:
            self.z.check_origin()
        except dns.zone.NoSOA:
            err = 'SOA RRset'
        except dns.zone.NoNS:
            err = 'NS RRset'
        except KeyError:
            err = 'origin node'
        if err:
            l.error('% {} has no {}'.format(self.zone_name, err))
            runner.send_msg('% {} has no {}'.format(self.zone_name, err))

        l.debug('[loadZone: zone={}, AXFR of {} nodes done'.format(self.zone_name, len(self.z.keys())))
        first = True
        for k in self.z.keys():
            zn = name = str(k)
            if name == '@':
                name = ''
            self.d[row][0] = name
            if not first:
                addr = dns.reversename.to_address(dns.name.from_text(name))
                (net, host) = self.addNet(addr)
                l.debug('host={}, name={}, net={}'.format(host, name, net))
                self.d[row][4] = host
                self.d[row][5] = net
            first = False
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
                        elif srdatatype == 'PTR':
                            a = dns.reversename.to_address(k)
                            if zad.prefs.debug: print('{}  {}'.format(a, name))
                        elif srdatatype == 'SOA' and srdata.endswith('.arpa.'):
                            a = dns.reversename.to_address(self.zone_name)
                            if zad.prefs.debug: print('{}  {}'.format(a, self.zone_name))
                        await self.createZoneFromName(srdatatype, srdata)
                        row = row + 1
                        self.d.append(['', '', '', '', '', ''])
                    ##l.debug('.', end=' ', flush=True)
                ##l.debug('+', end=' ', flush=True)
        self.valid = True
        l.info('[loadZone: {} RRs out of {} nodes from zone {} loaded.]'.format(
                                                            row -2,
                                                            len(self.z.keys()),
                                                            self.zone_name))
        if zad.prefs.debug: logZones()
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
        if zad.prefs.debug: print('createZoneFromName: {} done'.format(fqdn))

    def getNetsFromPrefs(self):
        if not ip4Nets and zad.prefs.ip4_nets:
            for net in zad.prefs.ip4_nets:
                ip4Nets[net] = ipaddress.IPv4Network(net)
        if not ip6Nets and zad.prefs.ip6_nets:
            for net in zad.prefs.ip6_nets:
                ip6Nets[net] = ipaddress.IPv6Network(net)

    def addNet(self, address) -> (str, str):
        """
        return tuple of net and host as strings
        """

        if ':' in address:                              # IPv6
            if self.zone_name.endswith('in-addr.arpa.'):
                l.error('?IPv4 address {} in IPv6 zone {} - ignored'.format(address, self.zone_name))
                l.runner.send_msg('?IPv4 address {} in IPv6 zone {} - ignored'.format(address, self.zone_name))
                return ('', '')
            
            a = ipaddress.IPv6Address(address)
            for k, v in self.nets.items():              # { netname: netobject }
                if a in v:
                    return (k,
                            str(ipaddress.IPv6Address(int(a) & int(v.hostmask)))[2:])
            for k, v in ip6Nets.items():                # { netname: netobject }
                if a in v:
                    if not a in self.nets:
                        self.nets[k] = v
                    return (k,
                            str(ipaddress.IPv6Address(int(a) & int(v.hostmask)))[2:])
            try:
                n = ipaddress.IPv6Network((int(a) & self.default_net_mask, int(zad.prefs.default_ip6_prefix)))
            except ValueError:
                l.error('?ValueError: IPv6 address {} in IPv6 zone {}, with mask {}'.format(
                                                                address, self.zone_name, hex(self.default_net_mask)))
                l.runner.send_msg('?ValueError: IPv6 address {} in IPv6 zone {}, with mask {}'.format(
                                                                address, self.zone_name, hex(self.default_net_mask)))
                return ('', '')
            self.nets[str(n)] = n
            ip6Nets[str(n)] = n
            return (str(n),
                    str(ipaddress.IPv6Address(int(a) & int(n.hostmask)))[2:])

        elif '.' in address:                            # IPv4
            def trimmHost(addr, net):
                m = re.match(r'^(0\.)+(.*)', str(ipaddress.IPv4Address(int(addr) & int(net.hostmask))), re.A)
                return m

            if self.zone_name.endswith('ip6.arpa.'):
                l.error('?IPv6 address {} in IPv4 zone {} - ignored'.format(address, self.zone_name))
                l.runner.send_msg('?IPv6 address {} in IPv4 zone {} - ignored'.format(address, self.zone_name))
                return ('', '')
                
            a = ipaddress.IPv4Address(address)
            for k, v in self.nets.items():              # { netname: netobject }
                if a in v:
                    return (k,
                            trimmHost(a, v))
            for k, v in ip4Nets.items():                # { netname: netobject }
                if a in v:
                    if not a in self.nets:
                        self.nets[k] = v
                    return (k,
                            trimmHost(a, v))
            n = ipaddress.IPv4Network((int(a) & self.default_net_mask, int(zad.prefs.default_ip4_prefix)))
            self.nets[str(n)] = n
            ip4Nets[str(n)] = n
            return (str(n),
                    trimmHost(a, n))

        else:
            assert 1 == 2, 'Zone.addNet received invalid address "{}"'.format(address)


class DomainZone(Zone):
    def __init__(self, zone_name):
        self.init_by_subclass = True
        self.type = zad.common.ZTDOM
        super(DomainZone, self).__init__(zone_name)
        self.d = [['', '', '', '']]

    def data(self, row: int, column: int) -> str:
        if not self.z:
            self.loadZone()
        v = self.d[row][column]
        if not v: v = ''
        return str(v)

    async def loadZone(self, runner: RunThread):
        row = 0
        self.z = dns.zone.Zone(self.zone_name, relativize=False)
        runner.send_msg('Loading {} ...'.format(self.zone_name))
        ns = zad.prefs.ns_for_axfr
        ok = False

        try:
            l.info('[Loading zone {} from NS {}]'.format(self.zone_name, ns))
            await do_axfr(ns, self.z)
            ok = True
        except dns.xfr.TransferError:
            l.error('?loadZone: {} AXFR failed with NS={}'.format(self.zone_name, ns))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.zone_name))
        except BaseException:
            l.error('%loadZone: {} Error on AXFR with NS={}, \n because {} - {}'.format(self.zone_name,
                                                                                        ns,
                                                                                        sys.exc_info()[0].__name__,
                                                                                        str(sys.exc_info()[1])))
            runner.send_msg('%loadZone: {} Error on AXFR with NS={}, because {} - {}'.format(self.zone_name,
                                                                                        ns,
                                                                                        sys.exc_info()[0].__name__,
                                                                                        str(sys.exc_info()[1])))

        if not ok:
            l.error('?loadZone {} failed. Giving up.'.format(self.zone_name))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.zone_name))
            self.d = [['', '', '', ''], ['', '', '', '']]
            return

        err = ''
        try:
            self.z.check_origin()
        except dns.zone.NoSOA:
            err = 'SOA RRset'
        except dns.zone.NoNS:
            err = 'NS RRset'
        except KeyError:
            err = 'origin node'
        if err:
            l.error('% {} has no {}'.format(self.zone_name, err))
            runner.send_msg('% {} has no {}'.format(self.zone_name, err))

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
                        elif srdatatype == 'PTR':
                            a = dns.reversename.to_address(k)
                            if zad.prefs.debug: print('{}  {}'.format(a, name))
                        elif srdatatype == 'SOA' and srdata.endswith('.arpa.'):
                            a = dns.reversename.to_address(self.zone_name)
                            if zad.prefs.debug: print('{}  {}'.format(a, self.zone_name))
                        await self.createZoneFromName(srdatatype, srdata)
                        row = row + 1
                        self.d.append(['', '', '', ''])
                    ##l.debug('.', end=' ', flush=True)
                ##l.debug('+', end=' ', flush=True)
        self.valid = True
        l.info('[{} RRs out of {} nodes from zone {} parsed and linked.]'.format(
                                                            row -2,
                                                            len(self.z.keys()),
                                                            self.zone_name))
        if zad.prefs.debug: logZones()
        runner.send_msg('Loading of {} completed with {} RRs'.format(self.zone_name, row -2))
        runner.send_zone_loaded(self.zone_name)


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
            logZones()
            runner.send_msg('All zones loaded.')
            time.sleep(5)
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
            l.info('{}{}'.format(k, '[loaded]' if z.valid else ''))
            for n in z.nets.keys():
                l.info('        {}'.format(n))

def setupResolver(resolver_addresses):

    if not resolver_addresses:
        return
    
    dns.resolver.get_default_resolver()
    dns.resolver.default_resolver.nameservers = resolver_addresses
    dns.resolver.default_resolver.cache = dns.resolver.LRUCache()


def setup():
    setupResolver(zad.common.IP_RESOLVER)
