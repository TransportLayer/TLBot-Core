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
                self.commands[module.__name__] = []
                for command in module.TL_META["commands"]:
                    default_parameters = {
                        "owner": module.__name__,
                        "public": True,
                        "available": [],
                        "enable_all": True,
                        "enabled": [],
                        "use_permissions": True,
                        "permissions": 0,
                        "use_roles": False,
                        "roles": []
                    }
                    default_parameters.update(command)
                    self.commands[module.__name__].append(default_parameters)

    async def allowed_to_run(self, command, member, su_check=False):
        role_ids = await self.transportlayerbot.get_user_role_ids(member)
        permissions = await self.transportlayerbot.db.get_user_permissions(member.id, role_ids)
        if su_check:
            if permissions[1]:
                return True
        if command["use_permissions"]:
            if permissions[0] >= command["permissions"]:
                return True
        if command["use_roles"]:
            if not set(role_ids).isdisjoint(command["roles"]):
                return True
        return False

    async def run_command(self, name, message, args, su_check=False, force=False):
        for module in self.commands:
            for command in self.commands[module]:
                if name == command["name"]:
                    if force or await self.allowed_to_run(command, message.author, su_check):
                        await command["function"](self.transportlayerbot, message, args)
        for command in await self.transportlayerbot.db.command_find(name, message.server.id):
            if force or await self.allowed_to_run(command, message.author, su_check):
                await db_commander.run_db_command(self.transportlayerbot, message, args, command)

    async def parse_message(self, message):
        prefix = await self.transportlayerbot.db.server_get(message.server.id, "prefix")
        if message.content.startswith(prefix[0]):
            command, *args = message.content[1:].split()
            if command == "sudo":
                command, *args = args
                return command, args, True
            return command, args, False
        else:
            return None, None, None

    async def run_message(self, transportlayerbot, message):
        command, args, check_su = await self.parse_message(message)
        if command:
            await self.run_command(command, message, args, check_su)

    def hook(self):
        self.transportlayerbot.events["on_message_noprivate_nobot"][__name__] = [self.run_message]
