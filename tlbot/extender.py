###############################################################################
#   TransportLayerBot: Extension Loader - All-in-one modular bot for Discord  #
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

from TLLogger import logger
from os import makedirs, listdir
from importlib import import_module

log = logger.get_logger(__name__)

class Extender:
    def __init__(self, transportlayerbot):
        self.transportlayerbot = transportlayerbot
        try:
            makedirs("plugins")
            log.warn("Plugins directory not found")
            log.warn("Created plugins directory")
        except:
            pass

        self.modules  = []
        for file in listdir("plugins"):
            if file.endswith(".py"):
                self.modules.append(import_module(f"plugins.{file[:-3]}"))
                if not self.modules[-1].TL_META:
                    del(self.modules[-1])

        for module in self.modules:
            for key in module.TL_META:
                if key in self.transportlayerbot.events:
                    self.transportlayerbot.events[key][module.__name__] = []
                    for function in module.TL_META[key]:
                        self.transportlayerbot.events[key][module.__name__].append(function)
