###############################################################################
#   TransportLayerBot: Commander - All-in-one modular bot for Discord         #
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
from tlbot import db_commander

log = logger.get_logger(__name__)

class Commander:
    def __init__(self, transportlayerbot):
        self.transportlayerbot = transportlayerbot
        self.commands = {}

    def load(self):
        self.commands = {}
        for module in self.transportlayerbot.ext.modules:
            if "commands" in module.TL_META:
                self.commands[module.__name__] = module.TL_META["commands"]

    async def run_command(self, name, message, args):
        for module in self.commands:
            if name in self.commands[module]:
                await self.commands[module][name](self.transportlayerbot, message, args)
        for command in await self.transportlayerbot.db.command_find(name, message.server.id):
            await db_commander.run_db_command(self.transportlayerbot, message, args, command)

    async def parse_message(self, message):
        prefix = await self.transportlayerbot.db.server_get(message.server.id, "prefix")
        if message.content.startswith(prefix[0]):
            command, *args = message.content[1:].split()
            return command, args
        else:
            return None, None

    async def run_message(self, transportlayerbot, message):
        command, args = await self.parse_message(message)
        if command:
            await self.run_command(command, message, args)

    def hook(self):
        self.transportlayerbot.events["on_message_nobot"][__name__] = [self.run_message]
