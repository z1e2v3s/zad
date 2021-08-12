# zad

zad - zone adminstration

## INTRODUCTION

In times of DNSsec, edited zone files interfere with resigning activities of
the nameserver. To avoid inconsistency, zones are maintained by dynamic update
(RFC 2136).
zad provides a GUI for dynamic updates and zone visualisation to make address
and host name editing easy like zone file editing.
 
## ABOUT THIS RELEASE

This is a alpha release.
This version does not yet support dynamic updates,
it just explores the configured initial zone and traverses all referenced
zones. From all referenced zones of which the configured ns allows zone
transfer, zone data will be read and displayed.
In revers zones, referenced networks will be stored.
Prefix is either taken from configured net or from a default prefix.
Hosts are displayed relative to their net.

## INSTALLATION

With python3.9 installed:
pip install ajr.zad

Or from repository:
git clone https://c
### Documentation

See [zad.readthedocs.io](https://zad.readthedocs.io).

### Source

See [codeberg.org/ajr/zad](https://codeberg.org/ajr/zad).


