.. _installation:

.. toctree::

Installation
============


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

Also recommended is an IDE like PyCharm (Community Edition)

Portability
___________

zad is developed and maintained on macos 10.15 and FreeBSD 13,
but should run on all platforms, where python 3.9 is available and to which
PyQt5 has been ported, like Linux and Windows.



