.. _installation:

.. toctree::

Installation and Configuration
==============================


Installation
____________
        
With python3.9 installed:

  pip install zad

Or from repository:

  git clone https://codeberg.org/ajr/zad

  pip install -e zad


Requirements
____________

ddns is currently tested only with **bind9.16**, but should work with other bind9
versions. For compatibility issues with other name servers, open an issue here
`zad issues <https://codeberg.org/ajr/zad/issues>`_.

Packages, installed from pypi.org are:

* dnspython 2.1.0
* PyQt5 5.15.4
* qasync 0.17.0

For development, these additional packages are required:

* build 0.5.1
* qt5-applications 5.15.2.2.2
* PyQt5-stubs 5.15.2.0

Also recommended is an IDE like PyCharm 2021.1.3 (Community Edition)

Portability
___________

zad is developed and maintained on macos 10.15 and FreeBSD 13,
but should run on all platforms, where python 3.9 is available and to which
PyQt5 has been ported, like Linux and Windows.



Configuration
=============

The preferences or settings panel (invoked from main menu) has 4 tabs:

* General

  * Master Server: DNS server for dynamic updates (ddns).
    If no Server for Zone Transfer (AXFR) configured, then the master server
    is used for both ddns and AXFR. The latter is recommended to avoid
    confusing stale data being displayed after ddns because of AXFR delay.

    If no Master Server configured (as in the default configuration) then
    no ddns is possible.
  * ddns Key File: A bind9 TSIG keyfile, created with the ddns-confgen
    utility like so:


       ddns-keygen -a hmac-sha256 name


    where "name" is the key name, like "ddns-key". For none-bind-users,
    the key file looks so:


       key "ddns-key" {
      	 algorithm hmac-sha256;
      	 secret "some-fancy-key";
       };


  * Server for Zone Transfer: Zone data is pulled from this server.
  * Initial Domain: Initial AXFR done from this zone. Referenced zones
    are loaded thereafter. Zones with prefixes below /9 (IPv4) and
    /17 (IPv6) are ignored.
  * Default Prefix IPv4: Used for all reverse IPv4 zones, for which no net
    configured.
  * Default Prefix IPv6: Used for all reverse IPv6 zones, for which no net
    configured.
  * Logfile: All logging goes to this file.
  * Debug Log: Log debugging info into Logfile.


* IPv4 Nets: Networks in prefix notation (192.168/16) into which
  related zones are divided.


* IPv6 Nets: Networks in prefix notation (2a05:bec0:26:ff:1/80) into which
  related zones are divided.


* Ignored Zones: These zones are not loaded (by AXFR) during initial
  zone walk.


