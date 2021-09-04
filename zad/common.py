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

from enum import Enum


DEBUG = False

DEFAULT_LOG_PATH = '/tmp/zad.log'

IP_XFR_NS = "81.4.108.41"

IP_RESOLVER = []

INITIAL_DOMAIN = 'zonetransfer.me'

MAX_ZONES = 5

TIMEOUT_RETRIES = 0
TIMEOUT_SLEEP = 5

windowHeading = 'zad - DNS zone admin'
app_name = 'zad'

ZTIP4 = 4
ZTIP6 = 6
ZTDOM = 1

class SubnetType(Enum):
    subdomain = 1
    ip4Net = 2
    ip6Net = 3

