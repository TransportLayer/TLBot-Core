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
import branding
from TLLogger import logger
import bot

def main():
    parser = argparse.ArgumentParser(description=branding.name, epilog="This bot has Super Tux Powers.")
    parse_login = parser.add_mutually_exclusive_group(required=True)
    parse_login.add_argument("-t", "--token", type=str, metavar="TOKEN", dest="TOKEN", help="bot-user application token", action="store", required=False)
    parse_login.add_argument("-e", "--email", type=str, metavar="EMAIL", dest="EMAIL", help="user email", action="store", required=False)
    parser.add_argument("-p", "--password", type=str, metavar="PASSWORD", dest="PASSWORD", help="user password", action="store", required=False)
    parser.add_argument("-H", "--host", type=str, metavar="DB HOST", dest="DB_HOST", help="hostname or IP of database", action="store", default="127.0.0.1", required=False)
    parser.add_argument("-P", "--port", type=int, metavar="DB PORT", dest="DB_PORT", help="port of database", action="store", default=27017, required=False)
    parser.add_argument("-d", "--db", type=str, metavar="DATABASE", dest="DB_NAME", help="name of the database", action="store", default="TransportLayerBot", required=False)
    parser.add_argument("-l", "--log", type=str, metavar="LEVEL", dest="LOG_LEVEL", help="log level", action="store", default="INFO", required=False)
    parser.add_argument("-o", "--output", type=str, metavar="FILE", dest="LOG_FILE", help="log file", action="store", default="TransportLayerBot.log", required=False)
    SETTINGS = vars(parser.parse_args())

    if SETTINGS["EMAIL"] and not SETTINGS["PASSWORD"]:
        print("Cannot login without password.")
        return

    print("""Welcome to {}!
This software is licensed under the GNU Affero General Public License.
See the LICENSE file for details.
Get the source code: {}
{}""".format(branding.name, branding.source, branding.logo.format('')))

    logger.setup_logger(SETTINGS["LOG_LEVEL"], SETTINGS["LOG_FILE"])
    log = logger.get_logger(__name__)

    log.info("Starting {}".format(branding.name))



    client = bot.TransportLayerBot(
        DB_INFO = {
            "NAME": SETTINGS["DB_NAME"],
            "HOST": SETTINGS["DB_HOST"],
            "PORT": SETTINGS["DB_PORT"]
        }
    )
    if SETTINGS["TOKEN"]:
        client.run(SETTINGS["TOKEN"])
    else:
        client.run(SETTINGS["EMAIL"], SETTINGS["PASSWORD"])

if __name__ == "__main__":
    main()
