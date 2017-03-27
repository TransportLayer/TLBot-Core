#!/usr/bin/env python3.5

###############################################################################
#   TransportLayerBot: Core - All-in-one modular bot for Discord              #
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

def main():
    parser = argparse.ArgumentParser(description="TransportLayerBot", epilog="This bot has Super Tux Powers.")
    parser.add_argument("-l", "--log", type=str, metavar="LEVEL", dest="LOG_LEVEL", help="log level", action="store", default="INFO", required=False)
    parser.add_argument("-o", "--output", type=str, metavar="FILE", dest="LOG_FILE", help="log file", action="store", default="TransportLayerBot.log", required=False)
    SETTINGS = vars(parser.parse_args())

    log = logger.setup_logger(SETTINGS["LOG_LEVEL"], SETTINGS["LOG_FILE"], __name__)

    log.info("Starting.")

if __name__ == "__main__":
    main()
