.. _introduction:

.. toctree::

Introduction
============

zad is an OpenSource software tool, written in Python that is intended
to handle the administration of DNS zone data of small zones (< 1000 RRs).
"zad" stands for "zone administration".


Supported features
__________________

Currently zad can:

* starting with a configured domain zone, this and any referenced zones
  are loaded (via AXFR) and displayed via browsable tables.
* delete, add or update resource records of these zones via dynamic update
* check of semantic and syntax of entered resource record if OK clicked
* to give the user a feedback, the modified zone is re-read and displayed
* the graphical user interface has been designed to allow point and click
* this tries to avoid the requirement to re-enter any data already
  displayed in the tables
* to simplify maintenance of reverse zones (especially of IPv6 ones),
  containing networks can be configured, which allows to enter and modify
  host addresses, relative to the selected network
* if no network has been configured for a reverse zone, default prefixes
  are used
* report any transaction and errors in both the GUI and a logfile
* optionally can display debug information


Features currently worked on
____________________________

* Check button to check current contents of form fields for correctness
* Updating Host field from Name/Address field or vice versa on Check button.
* On double clickeng, inserting values from upper three table browsers into
  Rdata of form:


  * From Domain zone take fqdn of double clicked OwnerName.
  * From IPv4 or IPv6 zone convert host address to a absolute address and
    take it as argument for form/RData


* Searching resource sets by owner names


Motivation
__________


In times of DNSsec, editing zone files by hand (e.g. with bind9 inline-signing)
often interferes with resigning activities of the nameserver.
To avoid inconsistencies, zones should be maintained by dynamic update
(RFC 2136).

This project was started to help the administrator with transition from
maintenance of zones in flat files to maintenance of zones via
dynamic update.


.. image:: _static/zad.png

