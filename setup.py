# -*- coding: UTF-8 -*-
#
# This file is part of the zad app
#
# Copyright 2021-2022 Axel Rau
#
# Licensed under GPLv3 or LGPLv3 License, (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.gnu.org/licenses/gpl-3.0
#    https://www.gnu.org/licenses/lgpl-3.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Solution from Flavio Garcia <piraz@candango.org>
from setuptools import setup, find_packages


longdesc = '''
In times of DNSsec, edited zone files interfere with resigning activities of
the nameserver. To avoid inconsistency, zones are maintained by dynamic update
(RFC 2136).

zad provides a GUI for dynamic updates and zone visualisation to make address
and host name editing easy like zone file editing.
'''

setup(
    name="zad",
    version="1.0rc2",
    license="GNU General Public License Version 3",
    description=("A GUI tool for maintaining DNS zones via dynamic update"),
    long_description=longdesc,
    long_description_content_type="text/markdown",
    url="https://codeberg.org/ajr/zad",
    project_urls={
        "Bug Tracker": "https://codeberg.org/ajr/zad/issues",
        "Documentation": "https://zad.readthedocs.io"
    },
    author="Axel Rau>",
    author_email="axel.rau@chaos1.de",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Internet :: Name Service (DNS)",
        "Intended Audience :: System Administrators",
    ],
    packages=find_packages(include=['zad', 'zad.*']),
    install_requires=[
        "dnspython==2.1.0",
        "PyQt5==5.15.4",
        "qasync==0.17.0"
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            "zad = zad.app:run",
        ],
    },
)

