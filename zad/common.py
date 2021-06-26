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


DEBUG = False

DEFAULT_LOG_PATH = '/tmp/zad.log'

IP_XFR_NS = ['2001:4bd8:0:104:217:17:192:66', '217.17.192.66',  '2001:4860:4802:32::72', '216.239.32.114']

##IP_RESOLVER = ['2606:4700:4700::1111', '1.1.1.1', '2606:4700:4700::1001', '1.0.0.1']
IP_RESOLVER = []

INITIAL_DOMAIN = 'iks-jena.de'

MAX_ZONES = 5

TIMEOUT_RETRIES = 0
TIMEOUT_SLEEP = 5

windowHeading = 'za - DNS zone admin'
app_name = 'zad'
