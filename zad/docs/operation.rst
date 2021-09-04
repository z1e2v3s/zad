.. _operation:

.. toctree::

Operation
=========


zad binary should have been installed in the default directory for python binaries
on a desktop system (macos, unix with X-windows installed ofe MS windows).

Usually, you just type


    zad


on the command line.

Currently there are no command line options.


Configuration
-------------

The preferences or settings panel (invoked from main menu) has 4 tabs:

* General

  * Master Server: DNS server for dynamic updates (ddns).
    If no Server for Zone Transfer (AXFR) configured, then the master server
    is used for both ddns and AXFR. The latter is recommended to avoid
    confusing stale data being displayed after a ddns update because of AXFR delay.

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



  * Server for Zone Transfer: Zone data is pulled from this server. If this field is empty,
    master server is used.
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


Working with the Editor
-----------------------

* Selecting and displaying zone data


  * In the Edit-Zone area, select the zone in the upper combo box.
  * If it is a reverse zone, select the network in the lower combo box.
  * In the table, select the row with the resource record (RR), which to delete or to
    modify. For adding RRs, select a row with a similar RR.
  * The Editor form is filled with the selected data


* Deleting zone data


  * If no field in the form has been modified, clicking '-' deletes the RR
  * After reloading the table shows the zone data without the deled RR.


* Modifying zone data


  * Any formfield can be changed, which activates the 'OK' and the 'Reset' button.
  * 'OK' validates the modified data, deleted the old RR and adds the modified RR.
  * 'Reset' resets the fields to the values of the selected table row.
  * If there are more than one RR per name/address (node), then modifying name/address
    creates a new node with the new name.
  * Changing a name to an existing name, adds the changed RR to the existing name.
  * In case of a reverse zone, the host field can be changed, which updates the
    reverse address in the name/address field on 'OK' and vice versa.
  * If the (new) type is 'A' or 'AAAA', rdata can be filled by double clicking a row
    in the IPv6-Zone respective the IPv4-Zone table. rdata may then be modified.


* Adding zone data


  * Everything from 'Modifying zone data' applied here to, but:
  * Instead of 'OK', '+' must be clicked.
  * If the name/address field has not been changed, then a RR is added
    to the selected node.
  * If the name/address field has been changed, then there is no difference to
    'Modifying zone data'.


* Logging

  * Add modifying transactions are recorded in the log file.


