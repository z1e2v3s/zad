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

from PyQt5 import QtCore, QtWidgets
import logging
import sys

import zad.models.main
import zad.views.main

application: QtWidgets.QApplication = None
translator: QtCore.QTranslator = None
locale: QtCore.QLocale = None

settings: QtCore.QSettings = None


def run():

    setup()
    init_translations()
    init_logging(zad.common.DEFAULT_LOG_PATH)

    zad.models.settings.setup()
    zad.views.settings.setup()

    zad.models.main.setup()
    zad.views.main.setup()
    if zad.common.DEBUG: print('Before application.exec_()')
    sys.exit(application.exec_())


def setup():
    global application

    application = QtWidgets.QApplication(sys.argv)


def init_translations():
    """
    Loads translations for a given input app. If a scaling factor is defined for testing, we use
    our own subclass of QTranslator.
    """
    global application, translator, locale

    ##locale = QLocale(system())                    # set to system locale
    QtCore.QLocale.setDefault(QtCore.QLocale('en')) # ? set to English for now
    locale = QtCore.QLocale()


def init_logging(path:str):
    # info, warning and error goes to file and to console if DEBUG set
    # debug goes to console only (if DEBUG set)
    
    logger = logging.getLogger()
    if zad.common.DEBUG:
        stdout_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(stdout_formatter)

        logger.addHandler(stdout_handler)

    else:
        logger.setLevel(logging.INFO)
            
    file_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s', 
                              '%m-%d-%Y %H:%M:%S')

    file_handler = logging.FileHandler(path)  ##FIXME##
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
