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


import zad.models.settings


__author__ = "Axel Rau <axel.rau+zad@chaos1,de>"
__version__ = "1.0rc2"
__licence__ = "GNU General Public License Version 3"


def get_version():
    return __version__


def get_author():
    return __author__.split(" <")[0]


def get_author_email():
    return __author__.split(" <")[1][:-1]


prefs: zad.models.settings.Prefs


