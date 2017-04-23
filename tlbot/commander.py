###############################################################################
#   TransportLayerBot: Command Interface - All-in-one modular bot for Discord #
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
import os
import importlib

log = logger.get_logger(__name__)

class Interpretor:
    def __init__(self, TLBot):
        self.TLBot = TLBot

        # Low-level command loading
        try:
            os.makedirs("modules")
            log.warn("Module directory not found; new directory created")
        except:
            pass

        self.modules = []
        for file in os.listdir("modules"):
            if file.endswith(".py"):
                self.modules.append(importlib.import_module("modules.{}".format(file[:-3])))
        log.info("Imported {} modules pending initialisation".format(len(self.modules)))

        self.commands = {}
        for module in self.modules:
            if hasattr(module, "TL_META"):
                if "COMMANDS" in module.TL_META:
                    self.commands.update(module.TL_META["COMMANDS"])
        log.info("Modules initialised; {} commands pending initialisation".format(len(self.commands)))

    def verify_commands(self, server_id):
        for command in self.TLBot.db.command_get_all_module(server_id):
            if not command["name"] in self.commands:
                ok, e = self.TLBot.db.command_delete(command["name"], server_id)
                if not ok:
                    log.warn("Could not delete command {}: {}".format(command["name"], e))

    def init_commands(self, server_id):
        self.verify_commands(server_id)
        for command in self.commands:
            self.TLBot.db.command_create(server_id, command, "module")

    def init_commands_in_all_servers(self):
        for server_id in self.TLBot.db.server_get_all_ids():
            self.init_commands(server_id)
        log.info("Commands initialised")

    def get_server_id_from_message(self, message):
        return message.server.id if not message.channel.is_private else message.channel.id

    async def run_command(self, command_details, message, args):
        if command_details["enabled"]:
            if command_details["type"] == "module":
                if command_details["name"] in self.commands:
                    await self.commands[command_details["name"]](self.TLBot, message, args)
                else:
                    log.warn("Command in database not in memory (is the module loaded?)")

    async def interpret(self, message):
        command, *args = message.content.split()
        server_id = self.get_server_id_from_message(message)
        server_details, e = self.TLBot.db.server_get(server_id)
        if server_details:
            if command.startswith(server_details["settings"]["prefix"]):
                command = command[len(server_details["settings"]["prefix"]):]
                command_details, e = self.TLBot.db.command_get(command, server_id)
                if command_details:
                    await self.run_command(command_details, message, args)
                else:
                    log.info("Cound not load command: {}".format(e))
        else:
            log.warn("Message sent in non-existent server")
