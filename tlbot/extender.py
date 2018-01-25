###############################################################################
#   TransportLayerBot: Extension Loader - All-in-one modular bot for Discord  #
#   Copyright (C) 2017, 2018  TransportLayer                                  #
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

    def load(self):
        self.modules  = []
        for file in listdir("plugins"):
            if file.endswith(".py"):
                try:
                    self.modules.append(import_module(f"plugins.{file[:-3]}"))
                    if not hasattr(self.modules[-1], "TL_META"):
                        log.error(f"Refusing to import {file} (could not find valid metadata)")
                        del(self.modules[-1])
                    else:
                        log.info(f"Imported {file}")
                except ModuleNotFoundError:
                    log.exception(f"Could not import {file} (is the filename valid?)")
                    log.error("Note that some characters (such as .) can cause this issue")
                except Exception:
                    log.exception(f"Error while importing {file}")
                    log.error("You may need to provide the information above to the plugin author")

        for module in self.modules:
            if "handlers" in module.TL_META:
                for handler in module.TL_META["handlers"]:
                    for function in module.TL_META["handlers"][handler]:
                        self.transportlayerbot.loop.create_task(self.transportlayerbot.add_handler(module.__name__, handler, function))
            if "priority_handlers" in module.TL_META:
                for handler in module.TL_META["priority_handlers"]:
                    for function in module.TL_META["priority_handlers"][handler]:
                        self.transportlayerbot.loop.create_task(self.transportlayerbot.add_handler(module.__name__, handler, function, priority=True))
