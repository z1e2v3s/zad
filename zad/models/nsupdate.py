import ipaddress
import logging
import re

import dns.query, dns.resolver, dns.rdatatype
import dns.exception, dns.rcode, dns.message
import dns.update, dns.tsigkeyring, dns.tsig

from PyQt5 import QtCore

import zad

l = logging.getLogger(__name__)

ddnsUpdate = None

class DdnsUpdate(QtCore.QObject):
    global l
    nsupdate_message = QtCore.pyqtSignal(str)           # lmessages for status bar

    def __init__(self, parent=None):
        super(DdnsUpdate, self).__init__(parent)

        self.master = zad.prefs.master_server
        self.keyring = self._get_ddns_keyring()
        return

    def _get_ddns_keyring(self) -> dns.tsigkeyring:
        """
        Read ddns key and return a key ring for dynamic DNS update
        :return: tsigkeyring
        """
        keyfile = zad.prefs.ddns_key_file
        if not keyfile and self.master:                 # none configured
            return

        key_name = secret = ''
        try:
            with open(keyfile) as kf:
                for line in kf:
                    key_name_match = re.search(r'key\s+"([-a-zA-Z]+)"', line, re.ASCII)
                    if key_name_match:
                        key_name = key_name_match.group(1)
                    secret_match = re.search(r'secret\s+"([=/a-zA-Z0-9]+)"', line, re.ASCII)
                    if secret_match:
                        secret = secret_match.group(1)
        except FileNotFoundError:
            self.error('?ddns key file not found - Check settings')
            return None
        if not (key_name and secret):
            self.error('Can''t parse ddns key file: {}{}'.
                            format('Bad key name ' if not key_name_match else '',
                                   'Bad secret' if not secret_match else ''))
            return None
        else:
            ddns_keyring = dns.tsigkeyring.from_text({key_name: secret})
            return ddns_keyring

    def error(self, message: str):
            l.error(message)
            self.nsupdate_message.emit(message)

    def handle(self, zone: str) -> dns.update.Update:
        """
        Obtain a dynamic DNS update instance
        :param zone: name of to update
        :return: dns.update.Update instance
        """

        if not self.keyring:
            self.error('No valid ddns keyfile configured. No ddns update operation possible')
            return False
        return dns.update.Update(zone,
                             keyring=self.keyring,
                             keyalgorithm=dns.tsig.HMAC_SHA256)


    def delete(self, zone_name, owner_name, rtype, rdata) -> bool:
        """
        Delete one RR
        """
        datatype = dns.rdatatype.from_text(rtype)
        update = self.handle(zone_name)
        if not update:
            return False
        update.delete(owner_name, datatype, rdata)
        response = dns.query.tcp(update, self.master)
        rc = response.rcode()
        if rc != dns.rcode.NOERROR:
            l.error('DNS delete operation failed for zone {} / {} {} {}:\n{} ({})'.
                  format(zone_name, owner_name, rtype, rdata, dns.rcode.to_text(rc), rc))
            return False
        else:
            l.info('[{} {} {} removed from zone {}]'.format(owner_name,  rtype, rdata, zone_name))
            self.nsupdate_message.emit('[{} {} {} removed from zone {}]'.format(owner_name, rtype, rdata, zone_name))
            return True

    def create(self, zone_name, owner_name, ttl, rtype, rdata) -> bool:
        ##datatype = dns.rdatatype.from_text(rtype)
        update = self.handle(zone_name)
        if not update:
            return False
        ##update.add(owner_name, datatype, rdata)
        update.add(owner_name, int(ttl), rtype, rdata)
        response: dns.message.Message = dns.query.tcp(update, self.master)
        rc: dns.rcode = response.rcode()
        if rc != dns.rcode.NOERROR:
            l.error('DNS add operation failed for zone {} / {} {} {}:\n{} ({})'.
                  format(zone_name, ttl, rtype, rdata, dns.rcode.to_text(rc), rc))
            return False
        else:
            l.info('[{} {} {} {} added to zone {}]'.format(owner_name, ttl, rtype, rdata, zone_name))
            self.nsupdate_message.emit('[{} {} {} {} added to zone {}]'.format(owner_name, ttl, rtype, rdata, zone_name))
            return True


def setup():
    global ddnsUpdate
    ddnsUpdate = DdnsUpdate()