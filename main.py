#!/usr/bin/env python3.6

###############################################################################
#   TransportLayerBot: Initialiser - All-in-one modular bot for Discord       #
#   Copyright (C) 2017  TransportLayer                                        #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as published  #
#   by the Free Software Foundation, either version 3 of the License, or      #
#   (at your option) any later version.                                       #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
###############################################################################

import argparse
from TLLogger import logger
from tlbot import branding
from tlbot import interface

def main():
    parser = argparse.ArgumentParser(description=branding.NAME_INTERNAL, epilog="This bot has Super Cow Powers.")
    parser.add_argument("-t", "--token", type=str, metavar="TOKEN", dest="TOKEN", help="bot application token", action="store", required=True)
    parser.add_argument("-H", "--host", type=str, metavar="DB HOST", dest="DB_HOST", help="hostname or IP of database", action="store", default="127.0.0.1", required=False)
    parser.add_argument("-P", "--port", type=int, metavar="DB PORT", dest="DB_PORT", help="port of database", action="store", default=27017, required=False)
    parser.add_argument("-d", "--db", type=str, metavar="DATABASE", dest="DB_NAME", help="name of the database", action="store", default="TransportLayerBot", required=False)
    parser.add_argument("-l", "--log", type=str, metavar="LEVEL", dest="LOG_LEVEL", help="log level", action="store", default="INFO", required=False)
    parser.add_argument("-o", "--output", type=str, metavar="FILE", dest="LOG_FILE", help="log file", action="store", default="TransportLayerBot.log", required=False)
    SETTINGS = vars(parser.parse_args())

    print(f"""Welcome to {branding.NAME_INTERNAL}!
This software is licensed under the GNU Affero General Public License.
See the LICENSE file for details.
Get the source code: {branding.SOURCE_CURRENT}""")
    print(branding.LOGO_FULL.format(tag=''))

    logger.setup_logger(SETTINGS["LOG_LEVEL"], SETTINGS["LOG_FILE"])
    log = logger.get_logger(__name__)

    log.info(f"Starting {branding.NAME_INTERNAL}")

    try:
        interface.start(SETTINGS)
    finally:
        log.info(f"{branding.NAME_INTERNAL} stopped")

if __name__ == "__main__":
    main()
    print(f"Thank you for using {branding.NAME_INTERNAL}. Goodbye.")
