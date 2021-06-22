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
import zad
from codecs import open
from pip._internal.req import parse_requirements
from pip._internal.network.session import PipSession
from setuptools import setup


with open("README.md", "r") as fd:
    long_description = fd.read()


# Solution from http://bit.ly/29Yl8VN
def resolve_requires(requirements_file):
    try:
        requirements = parse_requirements("./%s" % requirements_file,
                                          session=PipSession())
        return [str(ir.req) for ir in requirements]
    except AttributeError:
        # for pip >= 20.1.x
        # Need to run again as the first run was ruined by the exception
        requirements = parse_requirements("./%s" % requirements_file,
                                          session=PipSession())
        # pr stands for parsed_requirement
        return [str(pr.requirement) for pr in requirements]


setup(
    name="zad",
    version=zad.get_version(),
    license=zad.__licence__,
    description=("A GUI tool for maintaining DNS zones via dynamic update"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://codeberg.org/ajr/zad",
    project_urls = [
        "Bug Tracker = https://codeberg.org/ajr/zad/issues",
        "Documentation = https://codeberg.org/ajr/zad/issues"
    ],
    author=zad.get_author(),
    author_email=zad.get_author_email(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Internet :: Name Service (DNS)"
    ],
    packages=["zad"],
    install_requires=resolve_requires("requirements/basic.txt"),
    entry_points={
        'console_scripts': [
            "zad = zad.app:run",
        ],
    },
)

