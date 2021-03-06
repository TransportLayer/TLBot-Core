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
import signal
from os import kill
from discord import utils
from time import sleep

def client_thread(settings, pipe, queue):
    transportlayerbot = client.TransportLayerBot(tl_settings=settings, tl_queue=queue)

    def send_message(sig_num, stack):
        message = pipe.recv()
        channel = transportlayerbot.get_channel(message[0])
        transportlayerbot.loop.create_task(transportlayerbot.send_message(channel, message[1]))
    signal.signal(signal.SIGUSR1, send_message)

    try:
        transportlayerbot.loop.run_until_complete(transportlayerbot.start(settings["TOKEN"]))
    except KeyboardInterrupt:
        transportlayerbot.loop.run_until_complete(transportlayerbot.logout())
    finally:
        transportlayerbot.loop.close()

def start(settings):
    queue = multiprocessing.Queue()
    parent_pipe, child_pipe = multiprocessing.Pipe()

    thread = multiprocessing.Process(target=client_thread, args=(settings, child_pipe, queue,))
    thread.start()

    try:
        if settings["USE_INTERFACE"]:
            print("Interface not implemented")
            while True:
                if not queue.empty():
                    queue.get(block=False)
                sleep(0.05)
        else:
            while True:
                if not queue.empty():
                    queue.get(block=False)
                sleep(0.05)
    except KeyboardInterrupt:
        kill(thread.pid, signal.SIGINT)
