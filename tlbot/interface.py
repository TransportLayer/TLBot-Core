###############################################################################
#   TransportLayerBot: Interface - All-in-one modular bot for Discord         #
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

import multiprocessing
from tlbot import client
from signal import SIGINT
from os import kill
from TLLogger import logger

def client_thread(settings, queue):
    transportlayerbot = client.TransportLayerBot(tl_settings=settings, tl_queue=queue)
    transportlayerbot.run(settings["TOKEN"])

def start(settings):
    queue = multiprocessing.Queue()

    thread = multiprocessing.Process(target=client_thread, args=(settings, queue,))
    thread.start()

    try:
        while True: pass
    except KeyboardInterrupt:
        kill(thread.pid, SIGINT)
