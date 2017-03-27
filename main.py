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
import logging

def setup_logger(level_string, log_file):
    numeric_level = getattr(logging, level_string.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(level_string))

    verbose_formatter = logging.Formatter("[%(asctime)s] [%(name)s/%(levelname)s] %(message)s")
    file_formatter = verbose_formatter
    stdout_formatter = verbose_formatter if numeric_level == logging.DEBUG else logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

    root_logger = logging.getLogger(__name__)
    root_logger.setLevel(numeric_level)

    file_logger = logging.FileHandler(log_file)
    file_logger.setFormatter(file_formatter)
    root_logger.addHandler(file_logger)

    stdout_logger = logging.StreamHandler()
    stdout_logger.setFormatter(stdout_formatter)
    root_logger.addHandler(stdout_logger)

def main():
    parser = argparse.ArgumentParser(description="TransportLayerBot", epilog="This bot has Super Tux Powers.")
    parser.add_argument("-l", "--log", type=str, metavar="LEVEL", dest="LOG_LEVEL", help="log level", action="store", default="INFO", required=False)
    parser.add_argument("-o", "--output", type=str, metavar="FILE", dest="LOG_FILE", help="log file", action="store", default="TransportLayerBot.log", required=False)
    SETTINGS = vars(parser.parse_args())

    setup_logger(SETTINGS["LOG_LEVEL"], SETTINGS["LOG_FILE"])

    logger = logging.getLogger(__name__)
    logger.info("Starting.")

if __name__ == "__main__":
    main()
