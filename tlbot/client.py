###############################################################################
#   TransportLayerBot: Client - All-in-one modular bot for Discord            #
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
import discord
import asyncio
from time import time
from uuid import uuid4
from tlbot import extender

log = logger.get_logger(__name__)

class TransportLayerBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = {
            "on_ready": {},
            "on_resumed": {},
            "on_message": {},
            "on_message_send": {},
            "on_message_delete": {},
            "on_message_edit": {},
            "on_reaction_add": {},
            "on_reaction_remove": {},
            "on_reaction_clear": {},
            "on_channel_delete": {},
            "on_channel_create": {},
            "on_channel_update": {},
            "on_channel_pins_update": {},
            "on_member_join": {},
            "on_member_remove": {},
            "on_member_update": {},
            "on_server_join": {},
            "on_server_remove": {},
            "on_server_update": {},
            "on_server_role_create": {},
            "on_server_role_delete": {},
            "on_server_role_update": {},
            "on_server_emojis_update": {},
            "on_server_available": {},
            "on_server_unavailable": {},
            "on_voice_state_update": {},
            "on_member_ban": {},
            "on_member_unban": {},
            "on_typing": {},
            "on_group_join": {},
            "on_group_remove": {},
        }
        self.send_queue = {
            "backoff": 0,
            "queue": [],
            "servers": {},
            "results": {}
        }
        # DEBUG
        self.rate_limiter_running = False
        # END DEBUG
        ext = extender.Extender(self)


    # Event Handlers

    async def on_ready(self):
        for module in self.events["on_ready"]:
            for function in self.events["on_ready"][module]:
                await function(self)

    async def on_resumed(self):
        for module in self.events["on_resumed"]:
            for function in self.events["on_resumed"][module]:
                await function(self)

    async def on_message(self, message):
        for module in self.events["on_message"]:
            for function in self.events["on_message"][module]:
                await function(self, message)

    async def on_message_delete(self, message):
        for module in self.events["on_message_delete"]:
            for function in self.events["on_message_delete"][module]:
                await function(self, message)

    async def on_message_edit(self, before, after):
        for module in self.events["on_message_edit"]:
            for function in self.events["on_message_edit"][module]:
                await function(self, before, after)

    async def on_reaction_add(self, reaction, user):
        for module in self.events["on_reaction_add"]:
            for function in self.events["on_reaction_add"][module]:
                await function(self, reaction, user)

    async def on_reaction_remove(self, reaction, user):
        for module in self.events["on_reaction_remove"]:
            for function in self.events["on_reaction_remove"][module]:
                await function(self, reaction, user)

    async def on_reaction_clear(self, message, reactions):
        for module in self.events["on_reaction_clear"]:
            for function in self.events["on_reaction_clear"][module]:
                await function(self, message, reactions)

    async def on_channel_delete(self, channel):
        for module in self.events["on_channel_delete"]:
            for function in self.events["on_channel_delete"][module]:
                await function(self, channel)

    async def on_channel_create(self, channel):
        for module in self.events["on_channel_create"]:
            for function in self.events["on_channel_create"][module]:
                await function(self, channel)

    async def on_channel_update(self, before, after):
        for module in self.events["on_channel_update"]:
            for function in self.events["on_channel_update"][module]:
                await function(self, before, after)

    async def on_channel_pins_update(self, channel, last_pin):
        for module in self.events["on_channel_pins_update"]:
            for function in self.events["on_channel_pins_update"][module]:
                await function(self, channel, last_pin)

    async def on_member_join(self, member):
        for module in self.events["on_member_join"]:
            for function in self.events["on_member_join"][module]:
                await function(self, member)

    async def on_member_remove(self, member):
        for module in self.events["on_member_join"]:
            for function in self.events["on_member_join"][module]:
                await function(self, member)

    async def on_member_update(self, before, after):
        for module in self.events["on_member_update"]:
            for function in self.events["on_member_update"][module]:
                await function(self, before, after)

    async def on_server_join(self, server):
        for module in self.events["on_server_join"]:
            for function in self.events["on_server_join"][module]:
                await function(self, server)

    async def on_server_remove(self, server):
        for module in self.events["on_server_remove"]:
            for function in self.events["on_server_remove"][module]:
                await function(self, server)

    async def on_server_role_create(self, role):
        for module in self.events["on_server_role_create"]:
            for function in self.events["on_server_role_create"][module]:
                await function(self, role)

    async def on_server_role_delete(self, role):
        for module in self.events["on_server_role_delete"]:
            for function in self.events["on_server_role_delete"][module]:
                await function(self, role)

    async def on_server_role_update(self, before, after):
        for module in self.events["on_server_role_update"]:
            for function in self.events["on_server_role_update"][module]:
                await function(self, before, after)

    async def on_server_emojis_update(self, before, after):
        for module in self.events["on_server_emojis_update"]:
            for function in self.events["on_server_emojis_update"][module]:
                await function(self, before, after)

    async def on_server_available(self, server):
        for module in self.events["on_server_available"]:
            for function in self.events["on_server_available"][module]:
                await function(self, server)

    async def on_server_unavailable(self, server):
        for module in self.events["on_server_unavailable"]:
            for function in self.events["on_server_unavailable"][module]:
                await function(self, server)

    async def on_voice_state_update(self, before, after):
        for module in self.events["on_voice_state_update"]:
            for function in self.events["on_voice_state_update"][module]:
                await function(self, before, after)

    async def on_member_ban(self, member):
        for module in self.events["on_member_ban"]:
            for function in self.events["on_member_ban"][module]:
                await function(self, member)

    async def on_member_unban(self, server, user):
        for module in self.events["on_member_unban"]:
            for function in self.events["on_member_unban"][module]:
                await function(self, server, user)

    async def on_typing(self, channel, user, when):
        for module in self.events["on_typing"]:
            for function in self.events["on_typing"][module]:
                await function(self, channel, user, when)

    async def on_group_join(self, channel, user):
        for module in self.events["on_group_join"]:
            for function in self.events["on_group_join"][module]:
                await function(self, channel, user)

    async def on_group_remove(self, channel, user):
        for module in self.events["on_group_remove"]:
            for function in self.events["on_group_remove"][module]:
                await function(self, channel, user)


    # Request Proxies

    async def send_message(self, destination, content=None, *message, **kwargs):
        response = await super().send_message(destination, content, *message, **kwargs)
        for module in self.events["on_message_send"]:
            for function in self.events["on_message_send"][module]:
                await function(self, response)
        return response
