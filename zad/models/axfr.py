import asyncio
import ipaddress
import logging
import operator
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


# Subclasses, which store per net display data

class Ip4ZadNet(ipaddress.IPv4Network):

    def __init__(self, address, strict=True):
        super(Ip4ZadNet, self).__init__(address, strict)
        self.data = []

class Ip6ZadNet(ipaddress.IPv6Network):

    def __init__(self, address, strict=True):
        super(Ip6ZadNet, self).__init__(address, strict)
        self.data = []


class Zone(object):

    def zoneByName(zone_name):
        if zone_name.endswith('ip6.arpa.'):
            return ip6Zones[zone_name]
        elif zone_name.endswith('in-addr.arpa.'):
            return ip4Zones[zone_name]
        else:
            return domainZones[zone_name]
    
    def requestReload(zone_name):
        z = Zone.zoneByName(zone_name)
        z.valid = False

    def __init__(self, zone_name):
        global domainZones, ip4Zones, ip6Zones

        error = self.init_by_subclass   # bail out if not created as subclass
            
        self.name = zone_name
        if self.name[-1] != '.':
            self.name += '.'

        # add ourselves to globale zone list
        if self.type == zad.common.ZTIP6:
            ip6Zones[self.name] = self
        elif self.type == zad.common.ZTIP4:
            ip4Zones[self.name] = self
        elif self.type == zad.common.ZTDOM:
            domainZones[self.name] = self
        else:
            assert False,'?Wrong zone type "{}" in Zone __init__'.format(self.type)
            
        self.z = None
        self.valid = False
        self.unreachable = False
        self.ignored = self.name in zad.prefs.ignored_zones

        self.getNetsFromPrefs()
        
        self.nets = {}              # netname: ipaddress.IpNetwork object

        if self.name.endswith('ip6.arpa.'):
            self.default_net_mask = int(ipaddress.IPv6Network('1::/{}'.format(
                                                zad.prefs.default_ip6_prefix)).netmask)
            self.default_host_mask = int(ipaddress.IPv6Network('1::/{}'.format(
                                                zad.prefs.default_ip6_prefix)).hostmask)
        else:
            self.default_net_mask = int(Ip4ZadNet('1.0.0.0/{}'.format(
                                                zad.prefs.default_ip4_prefix)).netmask)
            self.default_host_mask = int(Ip4ZadNet('1.0.0.0/{}'.format(
                                                zad.prefs.default_ip4_prefix)).hostmask)


    def data(self, row: int, column: int) -> str:
        if not self.z:
            ## self.loadZone()          # FIXME: missing runner
            return ''
        v = self.d[row][column]
        if not v:
            v = ''
        return str(v)

    async def loadZone(self, runner: RunThread):
        """
        Inherited by Ip4Zone and Ip6Zone
        """

        # get zone data per zone transfer
        
        self.z = dns.zone.Zone(self.name, relativize=False)
        runner.send_msg('Loading {} ...'.format(self.name))
        ns = zad.prefs.ns_for_axfr if zad.prefs.ns_for_axfr else zad.prefs.master_server
        ok = False

        try:
            l.info('[Loading zone {} from NS {}]'.format(self.name, ns))
            await do_axfr(ns, self.z)
            ok = True
        except dns.xfr.TransferError:
            l.error('?loadZone: {} AXFR failed with NS={}'.format(self.name, ns))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.name))
        except BaseException:
            l.error('%loadZone: {} Error on AXFR with NS={}, \n because {} - {}'.format(self.name,
                                                                                        ns,
                                                                                        sys.exc_info()[0].__name__,
                                                                                        str(sys.exc_info()[1])))
            runner.send_msg('%loadZone: {} Error on AXFR with NS={}, because {} - {}'.format(self.name,
                                                                                        ns,
                                                                                        sys.exc_info()[0].__name__,
                                                                                        str(sys.exc_info()[1])))

        if not ok:
            l.error('?loadZone {} failed. Giving up.'.format(self.name))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.name))
            self.unreachable = True
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
            l.error('% {} has no {}'.format(self.name, err))
            runner.send_msg('% {} has no {}'.format(self.name, err))
            self.unreachable = True

        l.debug('[loadZone: zone={}, AXFR of {} nodes done'.format(self.name, len(self.z.keys())))

        # now parse and store zone data in a nested list (nodes)
        
        prefix = '0x' if self.name.endswith('.ip6.arpa.') else ''  #hex host addresses if IPv6
        nodes = []                                  # [host, rrs]   accumulated here
        first = True
        for k in self.z.keys():
            zn = name = str(k)
            if name == '@':
                name = self.name
            rrs = [['', '', '', '', '', '']]        # name, ttl, type, rdata, host, net
            i = 0                                   # index in rrs
            rrs[i][0] = name
            host = 0
            if not first:
                try:
                    addr = dns.reversename.to_address(dns.name.from_text(name))
                except dns.exception.SyntaxError:
                    l.error('? DNS error: Syntax error while converting reverse name {} to address'.format(name))
                    runner.send_msg('? DNS error: Syntax error while converting reverse name {} to address'.format(name))
                    self.unreachable = True
                    return
                (net, host) = self.addNet(addr)     # net_name, host as int
                l.debug('host={}, addr={}, net={}'.format(host, addr, net))
                if self.type == zad.common.ZTIP4:
                    rrs[i][4] = str(host)           # display IPv4 host
                else:
                    rrs[i][4] = hex(host)[2:]       # display IPv6 host in hex without "0x"
                rrs[i][5] = net
            first = False
            node = self.z[zn]
            for the_rdataset in node:               # rdatasets of current node collected in rrs
                rrs[i][1] = str(the_rdataset.ttl)
                for rdata in the_rdataset:
                    srdatatype = dns.rdatatype.to_text(the_rdataset.rdtype)
                    if srdatatype not in ('RRSIG', 'NSEC', 'NSEC3'):
                        rrs[i][2] = srdatatype
                        srdata = str(rdata)
                        rrs[i][3] = srdata
                        if srdatatype == 'MX':
                            srdata = str(rdata.exchange)
                        elif srdatatype == 'PTR':
                            a = dns.reversename.to_address(k)
                            ##if zad.prefs.debug: print('{}  {}'.format(a, name))
                        elif srdatatype == 'SOA' and srdata.endswith('.arpa.'):
                            a = dns.reversename.to_address(self.name)
                            ##if zad.prefs.debug: print('{}  {}'.format(a, self.name))
                        await self.createZoneFromName(srdatatype, srdata)
                        i = i + 1
                        rrs.append(['', '', '', '', '', ''])
                    ##l.debug('.', end=' ', flush=True)
                ##l.debug('+', end=' ', flush=True)

            if host:                                # host as int for sorting
                nodes.append((host, rrs))           # host, [related rdatasets]
            else:                                   # in apex
                nodes.append((0, rrs))              # origin, [related rdatasets]

        # sort by host number (decimal if IP4 or hex if IP6 [with prefix 0x])
        nodes.sort(key=lambda x: x[0])

        # now sort out net related nodes and store it as row list per net in net.data

        for net_name, net in self.nets.items():
            row = 0  # index in net.data
            net.data = [['', '', '', '', '']]
            first = True
            for node in nodes:
                (sort_host, rrs) = node
                for rr in rrs:
                    if first or rr[5] == net_name:
                        ##l.debug('row={}, rr={}'.format(repr(row), repr(rr)))

                        net.data[row][0] = rr[4]         # host number
                        net.data[row][1] = rr[0]         # origin name
                        net.data[row][2] = rr[1]         # ttl
                        net.data[row][3] = rr[2]         # rtype
                        net.data[row][4] = rr[3]         # rdata

                        net.data.append(['', '', '', '', ''])
                        row += 1
                first = False

            if zad.prefs.debug:
                logZones()
                runner.send_msg('Loading of {}, net {} completed with {} RRs'.format(
                                                                self.name, net_name, len(nodes)))

                l.debug('Loading of {}, net {} completed with {} RRs'.format(
                                                                self.name, net_name, len(nodes)))
        runner.send_zone_loaded(self.name)
        self.valid = True

    # create stub zone from rdata of RRs
    async def createZoneFromName(self, dtype, name):
        global domainZones, ip4Zones, ip6Zones

        if dtype in ('NS', 'MX', 'CNAME', 'DNAME', 'PTR', 'SRV'):   # a domain fqdn
            if name[-1] == '.':  # already absolute?
                fqdn = name
            else:               # no, relative - make absolute
                fqdn = name + '.' + self.name
            ## if len(domainZones.keys()) > zad.common.MAX_ZONES:
                ## return
        elif dtype == 'A':                                # address
            ## if len(ip4Zones.keys()) > zad.common.MAX_ZONES:
                ## return
            if name.count('.') < 3:                 # ignore everything below /9
                l.info('[Not creating reverse zone for {}, because below /9]'.format(name))
                return
            fqdn = dns.reversename.from_address(name)
        elif dtype == 'AAAA':                                # address
            ## if len(ip6Zones.keys()) > zad.common.MAX_ZONES:
                ## return
            if name.count(':') < 3:                 # ignore everything below /17
                l.info('[Not creating reverse zone for {}, because below /17]'.format(name))
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
        elif ( dtype in ('NS', 'MX', 'CNAME', 'DNAME', 'PTR', 'SRV')  and zoneName not in domainZones ):
            if zoneName.endswith('.arpa.'):
                l.error('?Unexpected reverse address (instead of name) {} in {} RR - ignored'.format(name, dtype))
                return

            domainZones[zoneName] = DomainZone(zoneName)
        if zad.prefs.debug: print('createZoneFromName: {} done'.format(fqdn))

    def getNetsFromPrefs(self):
        if not ip4Nets and zad.prefs.ip4_nets:
            for net_name in zad.prefs.ip4_nets:
                net = ipaddress.IPv4Network(net_name)
                ip4Nets[str(net)] = net            # use normalized form 2a05:bec0:26:: instead of 2a05:bec0:0026::
        if not ip6Nets and zad.prefs.ip6_nets:
            for net_name in zad.prefs.ip6_nets:
                net = ipaddress.IPv6Network(net_name)
                ip6Nets[str(net)] = net

    def addNet(self, address) -> (str, str):
        """
        return tuple of net as string and host as int
        """

        if ':' in address:                              # IPv6
            if self.type == zad.common.ZTIP4:
                l.error('?IPv6 address {} in IPv4 zone {} - ignored'.format(address, self.name))
                l.runner.send_msg('?IPv6 address {} in IPv4 zone {} - ignored'.format(address, self.name))
                return ('', 0)
            
            # try known nets of current zone
            a = ipaddress.IPv6Address(address)
            for k, v in self.nets.items():              # { netname: netobject }
                if a in v:
                    return (k,
                            int(ipaddress.IPv6Address(int(a) & int(v.hostmask))))
            # try all known nets, included those from settings
            for k, v in ip6Nets.items():                # { netname: netobject } but netname may be none-canonical
                if a in v:
                    self.nets[str(v)] = v               # none-canonical: 2a02:cd04:01:: instead of 2a02:cd04:1::
                    return (str(v),
                            int(ipaddress.IPv6Address(int(a) & int(v.hostmask))))
            # now create a new net from default prefix
            try:
                n = Ip6ZadNet((int(a) & self.default_net_mask, int(zad.prefs.default_ip6_prefix)))
            except ValueError:
                l.error('?ValueError: IPv6 address {} in IPv6 zone {}, with mask {}'.format(
                                                                address, self.name, hex(self.default_net_mask)))
                l.runner.send_msg('?ValueError: IPv6 address {} in IPv6 zone {}, with mask {}'.format(
                                                                address, self.name, hex(self.default_net_mask)))
                return ('', 0)
            self.nets[str(n)] = n
            ip6Nets[str(n)] = n
            return (str(n),
                    int(ipaddress.IPv6Address(int(a) & int(n.hostmask))))

        elif '.' in address:
            def trimmHost(addr, net):
                m = re.match(r'^(0\.)+(.*)', str(ipaddress.IPv4Address(int(addr) & int(net.hostmask))), re.A)
                return int(m.group(2))

            if self.type == zad.common.ZTIP6:
                l.error('?IPv4 address {} in IPv6 zone {} - ignored'.format(address, self.name))
                l.runner.send_msg('?IPv4 address {} in IPv6 zone {} - ignored'.format(address, self.name))
                return ('', 0)
                
            a = ipaddress.IPv4Address(address)
            for k, v in self.nets.items():              # { netname: netobject }
                if a in v:
                    return (k,
                            trimmHost(a, v))
            for k, v in ip4Nets.items():                # { netname: netobject }
                if a in v:
                    self.nets[k] = v
                    return (k,
                            trimmHost(a, v))
            n = Ip4ZadNet((int(a) & self.default_net_mask, int(zad.prefs.default_ip4_prefix)))
            self.nets[str(n)] = n
            ip4Nets[str(n)] = n
            return (str(n),
                    trimmHost(a, n))

        else:
            assert False, 'Zone.addNet received invalid address "{}"'.format(address)
            self.unreachable = True


class DomainZone(Zone):
    def __init__(self, zone_name):
        self.init_by_subclass = True
        self.type = zad.common.ZTDOM
        super(DomainZone, self).__init__(zone_name)
        self.d = [['', '', '', '', '']]

    def data(self, row: int, column: int) -> str:
        if not self.z:
            self.loadZone()
        v = self.d[row][column]
        if not v: v = ''
        return str(v)

    async def loadZone(self, runner: RunThread):
        row = 0
        self.d = [['', '', '', '', '']]
        self.z = dns.zone.Zone(self.name, relativize=False)
        runner.send_msg('Loading {} ...'.format(self.name))
        ns = zad.prefs.ns_for_axfr if zad.prefs.ns_for_axfr else zad.prefs.master_server
        ok = False

        try:
            l.info('[Loading zone {} from NS {}]'.format(self.name, ns))
            await do_axfr(ns, self.z)
            ok = True
        except dns.xfr.TransferError:
            l.error('?loadZone: {} AXFR failed with NS={}'.format(self.name, ns))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.name))
        except BaseException:
            l.error('%loadZone: {} Error on AXFR with NS={}, \n because {} - {}'.format(self.name,
                                                                                        ns,
                                                                                        sys.exc_info()[0].__name__,
                                                                                        str(sys.exc_info()[1])))
            runner.send_msg('%loadZone: {} Error on AXFR with NS={}, because {} - {}'.format(self.name,
                                                                                        ns,
                                                                                        sys.exc_info()[0].__name__,
                                                                                        str(sys.exc_info()[1])))

        if not ok:
            l.error('?loadZone {} failed. Giving up.'.format(self.name))
            runner.send_msg('?loadZone {} failed. Giving up.'.format(self.name))
            self.unreachable = True
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
            l.error('% {} has no {}'.format(self.name, err))
            runner.send_msg('% {} has no {}'.format(self.name, err))

        l.debug('[loadZone: zone={}, AXFR of {} nodes done'.format(self.name, len(self.z.keys())))
        for k in self.z.keys():
            zn = name = str(k)
            if name == '@': name = ''
            self.d[row][1] = name
            node = self.z[zn]
            for the_rdataset in node:
                self.d[row][2] = str(the_rdataset.ttl)
                for rdata in the_rdataset:
                    srdatatype = dns.rdatatype.to_text(the_rdataset.rdtype)
                    if srdatatype not in ('RRSIG', 'NSEC', 'NSEC3'):
                        self.d[row][3] = srdatatype
                        srdata = str(rdata)
                        self.d[row][4] = srdata
                        try:
                            if srdatatype == 'MX':
                                srdata = str(rdata.exchange)
                            elif srdatatype == 'PTR':
                                a = dns.reversename.to_address(k)
                                ##if zad.prefs.debug: print('{}  {}'.format(a, name))
                            elif srdatatype == 'SOA' and srdata.endswith('.arpa.'):
                                a = dns.reversename.to_address(self.name)
                                ##if zad.prefs.debug: print('{}  {}'.format(a, self.name))
                        except dns.exception.SyntaxError:
                            l.error('%Malformed rdata: {} {} {}'.format(name, srdatatype, srdata))
                            runner.send_msg('%Malformed rdata: {} {} {}'.format(name, srdatatype, srdata))

                        else:
                            await self.createZoneFromName(srdatatype, srdata)
                        row = row + 1
                        self.d.append(['', '', '', '', ''])             # host(unused), name, ttl, type, rdata
                    ##l.debug('.', end=' ', flush=True)
                ##l.debug('+', end=' ', flush=True)
        self.valid = True
        l.info('[{} RRs out of {} nodes from zone {} parsed and linked.]'.format(
                                                            row -2,
                                                            len(self.z.keys()),
                                                            self.name))
        if zad.prefs.debug: logZones()
        runner.send_msg('Loading of {} completed with {} RRs'.format(self.name, row -2))
        runner.send_zone_loaded(self.name)


class Ip4Zone(Zone):
    def __init__(self, zone_name):
        self.init_by_subclass = True
        self.type = zad.common.ZTIP4
        super(Ip4Zone, self).__init__(zone_name)


class Ip6Zone(Zone):
    def __init__(self, zone_name):
        self.init_by_subclass = True
        self.type = zad.common.ZTIP6
        super(Ip6Zone, self).__init__(zone_name)


async def loadZones(runner: RunThread):
    """
    Check for zones which not have been loaded and load them
    """
    first_run_done = False
    def find_next_zone():
        zone_list = []
        for d in (domainZones, ip4Zones, ip6Zones):
            for k in d.keys():
                z = d[k]
                ## if len(z.d) < 2:
                if not z.valid and not z.unreachable and not z.ignored:
                    zone_list.append((z))
        if zone_list:
            return zone_list[0]
        else:
            return None

    while True:
        z = find_next_zone()
        if z:
            ## if first_run_done:              # zone has been modified by zad
            ##     await asyncio.sleep(10)      # allow for notify/axfr delay
            await z.loadZone(runner)
        else:
            if not first_run_done:
                logZones()
                runner.send_msg('All zones loaded.')
                first_run_done = True
            time.sleep(2)

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
