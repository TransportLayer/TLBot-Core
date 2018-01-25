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
from copy import deepcopy
from tlbot import extender
from tlbot import commander
from tlbot import db_tools

log = logger.get_logger(__name__)

class TransportLayerBot(discord.Client):
    def __init__(self, *args, tl_settings, tl_queue, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = tl_queue
        self.db = {
            "name": tl_settings["DB_NAME"],
            "host": tl_settings["DB_HOST"],
            "port": tl_settings["DB_PORT"]
        }
        self.loop_time = 0.5
        self.events = {
            "on_ready": {},
            "on_bot_ready": {},
            "on_resumed": {},
            "on_message": {},
            "on_message_noself": {},
            "on_message_nobot": {},
            "on_message_noprivate": {},
            "on_message_noprivate_noself": {},
            "on_message_noprivate_nobot": {},
            "on_message_private": {},
            "on_message_private_noself": {},
            "on_message_send": {},
            "on_message_send_noprivate": {},
            "on_message_send_private": {},
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
        self.on_bot_ready_run = False
        self.priority_events = deepcopy(self.events)
        self.user_choices = {}
        self.ext = extender.Extender(self)
        self.ext.load()
        self.cmd = commander.Commander(self)
        self.cmd.hook()
        self.cmd.load()


    # Database connection
    async def connect(self):
        self.db = db_tools.BotDatabase(name=self.db["name"], host=self.db["host"], port=self.db["port"])
        await super().connect()


    # Event Handlers

    async def on_ready(self):
        # Queue updater
        self.queue.put(
            {
                "event": "on_ready"
            }
        )

        # Server member state tracker
        last_state = await self.db.server_get_ids({"member": True})
        for server in self.servers:
            if not server.id in last_state:
                await self.db.server_join(server.id)
            elif server.id in last_state:
                last_state.remove(server.id)
        for server in last_state:
            await self.db.server_leave(server.id)

        # Priority Event Handler
        if not self.on_bot_ready_run:
            for module in self.priority_events["on_bot_ready"]:
                for function in self.priority_events["on_bot_ready"][module]:
                    await function(self)
        for module in self.priority_events["on_ready"]:
            for function in self.priority_events["on_ready"][module]:
                await function(self)
        # Standard Event Handler
        if not self.on_bot_ready_run:
            for module in self.events["on_bot_ready"]:
                for function in self.events["on_bot_ready"][module]:
                    await function(self)
        for module in self.events["on_ready"]:
            for function in self.events["on_ready"][module]:
                await function(self)

        self.on_bot_ready_run = True

    async def on_resumed(self):
        # Queue updater
        self.queue.put(
            {
                "event": "on_resumed"
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_resumed"]:
            for function in self.priority_events["on_resumed"][module]:
                await function(self)
        # Standard Event Handler
        for module in self.events["on_resumed"]:
            for function in self.events["on_resumed"][module]:
                await function(self)

    async def on_message(self, message):
        # Queue updater
        self.queue.put(
            {
                "event": "on_message",
                "message": message
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_message"]:
            for function in self.priority_events["on_message"][module]:
                await function(self, message)
        # Standard Event Handler
        for module in self.events["on_message"]:
            for function in self.events["on_message"][module]:
                await function(self, message)
        # Special Handlers
        if not message.author == self.user:
            # Priority Event Handler
            for module in self.priority_events["on_message_noself"]:
                for function in self.priority_events["on_message_noself"][module]:
                    await function(self, message)
            for module in self.events["on_message_noself"]:
                for function in self.events["on_message_noself"][module]:
                    await function(self, message)
        if not message.author.bot:
            # Priority Event Handler
            for module in self.priority_events["on_message_nobot"]:
                for function in self.priority_events["on_message_nobot"][module]:
                    await function(self, message)
            # Standard Event Handler
            for module in self.events["on_message_nobot"]:
                for function in self.events["on_message_nobot"][module]:
                    await function(self, message)
        if not message.channel.is_private == self.user:
            # Priority Event Handler
            for module in self.priority_events["on_message_noprivate"]:
                for function in self.priority_events["on_message_noprivate"][module]:
                    await function(self, message)
            # Standard Event Handler
            for module in self.events["on_message_noprivate"]:
                for function in self.events["on_message_noprivate"][module]:
                    await function(self, message)
        if not message.channel.is_private and not message.author == self.user:
            # Priority Event Handler
            for module in self.priority_events["on_message_noprivate_noself"]:
                for function in self.priority_events["on_message_noprivate_noself"][module]:
                    await function(self, message)
            # Standard Event Handler
            for module in self.events["on_message_noprivate_noself"]:
                for function in self.events["on_message_noprivate_noself"][module]:
                    await function(self, message)
        if not message.channel.is_private and not message.author.bot:
            # Priority Event Handler
            for module in self.priority_events["on_message_noprivate_nobot"]:
                for function in self.priority_events["on_message_noprivate_nobot"][module]:
                    await function(self, message)
            # Standard Event Handler
            for module in self.events["on_message_noprivate_nobot"]:
                for function in self.events["on_message_noprivate_nobot"][module]:
                    await function(self, message)
        if message.channel.is_private:
            # Priority Event Handler
            for module in self.priority_events["on_message_private"]:
                for function in self.priority_events["on_message_private"][module]:
                    await function(self, message)
            # Standard Event Handler
            for module in self.events["on_message_private"]:
                for function in self.events["on_message_private"][module]:
                    await function(self, message)
        if message.channel.is_private and not message.author == self.user:
            # Priority Event Handler
            for module in self.priority_events["on_message_private_noself"]:
                for function in self.priority_events["on_message_private_noself"][module]:
                    await function(self, message)
            # Standard Event Handler
            for module in self.events["on_message_private_noself"]:
                for function in self.events["on_message_private_noself"][module]:
                    await function(self, message)

    async def on_message_delete(self, message):
        # Queue updater
        self.queue.put(
            {
                "event": "on_message_delete",
                "message": message
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_message_delete"]:
            for function in self.priority_events["on_message_delete"][module]:
                await function(self, message)
        # Standard Event Handler
        for module in self.events["on_message_delete"]:
            for function in self.events["on_message_delete"][module]:
                await function(self, message)

    async def on_message_edit(self, before, after):
        # Queue updater
        self.queue.put(
            {
                "event": "on_message_edit",
                "before": before,
                "after": after
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_message_edit"]:
            for function in self.priority_events["on_message_edit"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_message_edit"]:
            for function in self.events["on_message_edit"][module]:
                await function(self, before, after)

    async def on_reaction_add(self, reaction, user):
        # Queue updater
        self.queue.put(
            {
                "event": "on_reaction_add",
                "reaction": reaction,
                "user": user
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_reaction_add"]:
            for function in self.priority_events["on_reaction_add"][module]:
                await function(self, reaction, user)
        # Standard Event Handler
        for module in self.events["on_reaction_add"]:
            for function in self.events["on_reaction_add"][module]:
                await function(self, reaction, user)

    async def on_reaction_remove(self, reaction, user):
        # Queue updater
        self.queue.put(
            {
                "event": "on_reaction_remove",
                "reaction": reaction,
                "user": user
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_reaction_remove"]:
            for function in self.priority_events["on_reaction_remove"][module]:
                await function(self, reaction, user)
        # Standard Event Handler
        for module in self.events["on_reaction_remove"]:
            for function in self.events["on_reaction_remove"][module]:
                await function(self, reaction, user)

    async def on_reaction_clear(self, message, reactions):
        # Queue updater
        self.queue.put(
            {
                "event": "on_reaction_clear",
                "message": message,
                "reactions": reactions
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_reaction_clear"]:
            for function in self.priority_events["on_reaction_clear"][module]:
                await function(self, message, reactions)
        # Standard Event Handler
        for module in self.events["on_reaction_clear"]:
            for function in self.events["on_reaction_clear"][module]:
                await function(self, message, reactions)

    async def on_channel_delete(self, channel):
        # Queue updater
        self.queue.put(
            {
                "event": "on_channel_delete",
                "channel": channel
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_channel_delete"]:
            for function in self.priority_events["on_channel_delete"][module]:
                await function(self, channel)
        # Standard Event Handler
        for module in self.events["on_channel_delete"]:
            for function in self.events["on_channel_delete"][module]:
                await function(self, channel)

    async def on_channel_create(self, channel):
        # Queue updater
        self.queue.put(
            {
                "event": "on_channel_create",
                "channel": channel
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_channel_create"]:
            for function in self.priority_events["on_channel_create"][module]:
                await function(self, channel)
        # Standard Event Handler
        for module in self.events["on_channel_create"]:
            for function in self.events["on_channel_create"][module]:
                await function(self, channel)

    async def on_channel_update(self, before, after):
        # Queue updater
        self.queue.put(
            {
                "event": "on_channel_update",
                "before": before,
                "after": after
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_channel_update"]:
            for function in self.priority_events["on_channel_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_channel_update"]:
            for function in self.events["on_channel_update"][module]:
                await function(self, before, after)

    async def on_channel_pins_update(self, channel, last_pin):
        # Queue updater
        self.queue.put(
            {
                "event": "on_channel_pins_update",
                "channel": channel,
                "last_pin": last_pin
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_channel_pins_update"]:
            for function in self.priority_events["on_channel_pins_update"][module]:
                await function(self, channel, last_pin)
        # Standard Event Handler
        for module in self.events["on_channel_pins_update"]:
            for function in self.events["on_channel_pins_update"][module]:
                await function(self, channel, last_pin)

    async def on_member_join(self, member):
        # Queue updater
        self.queue.put(
            {
                "event": "on_member_join",
                "member": member
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_member_join"]:
            for function in self.priority_events["on_member_join"][module]:
                await function(self, member)
        # Standard Event Handler
        for module in self.events["on_member_join"]:
            for function in self.events["on_member_join"][module]:
                await function(self, member)

    async def on_member_remove(self, member):
        # Queue updater
        self.queue.put(
            {
                "event": "on_member_remove",
                "member": member
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_member_remove"]:
            for function in self.priority_events["on_member_remove"][module]:
                await function(self, member)
        # Standard Event Handler
        for module in self.events["on_member_remove"]:
            for function in self.events["on_member_remove"][module]:
                await function(self, member)

    async def on_member_update(self, before, after):
        # Queue updater
        self.queue.put(
            {
                "event": "on_member_update",
                "before": before,
                "after": after
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_member_update"]:
            for function in self.priority_events["on_member_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_member_update"]:
            for function in self.events["on_member_update"][module]:
                await function(self, before, after)

    async def on_server_join(self, server):
        # Queue updater
        self.queue.put(
            {
                "event": "on_server_join",
                "server": server
            }
        )

        # Priority Event Handler
        await self.db.server_join(server.id)
        for module in self.priority_events["on_server_join"]:
            for function in self.priority_events["on_server_join"][module]:
                await function(self, server)
        # Standard Event Handler
        await self.db.server_join(server.id)
        for module in self.events["on_server_join"]:
            for function in self.events["on_server_join"][module]:
                await function(self, server)

    async def on_server_remove(self, server):
        # Queue updater
        self.queue.put(
            {
                "event": "on_server_remove",
                "server": server
            }
        )

        # Priority Event Handler
        await self.db.server_leave(server.id)
        for module in self.priority_events["on_server_remove"]:
            for function in self.priority_events["on_server_remove"][module]:
                await function(self, server)
        # Standard Event Handler
        await self.db.server_leave(server.id)
        for module in self.events["on_server_remove"]:
            for function in self.events["on_server_remove"][module]:
                await function(self, server)

    async def on_server_role_create(self, role):
        # Queue updater
        self.queue.put(
            {
                "event": "on_server_role_create",
                "role": role
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_server_role_create"]:
            for function in self.priority_events["on_server_role_create"][module]:
                await function(self, role)
        # Standard Event Handler
        for module in self.events["on_server_role_create"]:
            for function in self.events["on_server_role_create"][module]:
                await function(self, role)

    async def on_server_role_delete(self, role):
        # Queue updater
        self.queue.put(
            {
                "event": "on_server_role_delete",
                "role": role
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_server_role_delete"]:
            for function in self.priority_events["on_server_role_delete"][module]:
                await function(self, role)
        # Standard Event Handler
        for module in self.events["on_server_role_delete"]:
            for function in self.events["on_server_role_delete"][module]:
                await function(self, role)

    async def on_server_role_update(self, before, after):
        # Queue updater
        self.queue.put(
            {
                "event": "on_server_role_update",
                "before": before,
                "after": after
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_server_role_update"]:
            for function in self.priority_events["on_server_role_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_server_role_update"]:
            for function in self.events["on_server_role_update"][module]:
                await function(self, before, after)

    async def on_server_emojis_update(self, before, after):
        # Queue updater
        self.queue.put(
            {
                "event": "on_server_emojus_update",
                "before": before,
                "after": after
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_server_emojis_update"]:
            for function in self.priority_events["on_server_emojis_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_server_emojis_update"]:
            for function in self.events["on_server_emojis_update"][module]:
                await function(self, before, after)

    async def on_server_available(self, server):
        # Queue updater
        self.queue.put(
            {
                "event": "on_server_available",
                "server": server
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_server_available"]:
            for function in self.priority_events["on_server_available"][module]:
                await function(self, server)
        # Standard Event Handler
        for module in self.events["on_server_available"]:
            for function in self.events["on_server_available"][module]:
                await function(self, server)

    async def on_server_unavailable(self, server):
        # Queue updater
        self.queue.put(
            {
                "event": "on_server_unavailable",
                "server": server
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_server_unavailable"]:
            for function in self.priority_events["on_server_unavailable"][module]:
                await function(self, server)
        # Standard Event Handler
        for module in self.events["on_server_unavailable"]:
            for function in self.events["on_server_unavailable"][module]:
                await function(self, server)

    async def on_voice_state_update(self, before, after):
        # Queue updater
        self.queue.put(
            {
                "event": "on_voice_state_update",
                "before": before,
                "after": after
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_voice_state_update"]:
            for function in self.priority_events["on_voice_state_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_voice_state_update"]:
            for function in self.events["on_voice_state_update"][module]:
                await function(self, before, after)

    async def on_member_ban(self, member):
        # Queue updater
        self.queue.put(
            {
                "event": "on_member_ban",
                "member": member
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_member_ban"]:
            for function in self.priority_events["on_member_ban"][module]:
                await function(self, member)
        # Standard Event Handler
        for module in self.events["on_member_ban"]:
            for function in self.events["on_member_ban"][module]:
                await function(self, member)

    async def on_member_unban(self, server, user):
        # Queue updater
        self.queue.put(
            {
                "event": "on_member_unban",
                "server": server,
                "user": user
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_member_unban"]:
            for function in self.priority_events["on_member_unban"][module]:
                await function(self, server, user)
        # Standard Event Handler
        for module in self.events["on_member_unban"]:
            for function in self.events["on_member_unban"][module]:
                await function(self, server, user)

    async def on_typing(self, channel, user, when):
        # Queue updater
        self.queue.put(
            {
                "event": "on_typing",
                "channel": channel,
                "user": user,
                "when": when
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_typing"]:
            for function in self.priority_events["on_typing"][module]:
                await function(self, channel, user, when)
        # Standard Event Handler
        for module in self.events["on_typing"]:
            for function in self.events["on_typing"][module]:
                await function(self, channel, user, when)

    async def on_group_join(self, channel, user):
        # Queue updater
        self.queue.put(
            {
                "event": "on_group_join",
                "channel": channel,
                "user": user
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_group_join"]:
            for function in self.priority_events["on_group_join"][module]:
                await function(self, channel, user)
        # Standard Event Handler
        for module in self.events["on_group_join"]:
            for function in self.events["on_group_join"][module]:
                await function(self, channel, user)

    async def on_group_remove(self, channel, user):
        # Queue updater
        self.queue.put(
            {
                "event": "on_group_remove",
                "channel": channel,
                "user": user
            }
        )

        # Priority Event Handler
        for module in self.priority_events["on_group_remove"]:
            for function in self.priority_events["on_group_remove"][module]:
                await function(self, channel, user)
        # Standard Event Handler
        for module in self.events["on_group_remove"]:
            for function in self.events["on_group_remove"][module]:
                await function(self, channel, user)


    # Request Proxies

    async def send_message(self, destination, content=None, *message, **kwargs):
        response = await super().send_message(destination, content, *message, **kwargs)
        # Priority Event Handler
        for module in self.priority_events["on_message_send"]:
            for function in self.priority_events["on_message_send"][module]:
                await function(self, response)
        # Standard Event Handler
        for module in self.events["on_message_send"]:
            for function in self.events["on_message_send"][module]:
                await function(self, response)
        # Special Handlers
        if not response.channel.is_private:
            # Priority Event Handler
            for module in self.priority_events["on_message_send_noprivate"]:
                for function in self.priority_events["on_message_send_noprivate"][module]:
                    await function(self, response)
            # Standard Event Handler
            for module in self.events["on_message_send_noprivate"]:
                for function in self.events["on_message_send_noprivate"][module]:
                    await function(self, response)
        if response.channel.is_private:
            # Priority Event Handler
            for module in self.priority_events["on_message_send_private"]:
                for function in self.priority_events["on_message_send_private"][module]:
                    await function(self, response)
            # Standard Event Handler
            for module in self.events["on_message_send_private"]:
                for function in self.events["on_message_send_private"][module]:
                    await function(self, response)
        return response


    # Utility Functions
    async def add_handler(self, module_name, handler, function, priority=False):
        if priority:
            events = self.priority_events
        else:
            events = self.events

        if not module_name in events[handler]:
            events[handler][module_name] = []
        events[handler][module_name].append(function)

    async def get_user_role_ids(self, member):
        roles = []
        for role in member.roles:
            roles.append(role.id)
        return roles

    async def wait_for_choice(self, messages, options=['✅', '❌'], users=None, timeout=None, first=True, return_on=['✅'], limit=0):
        for message in messages:
            for emoji in options:
                await self.add_reaction(message, emoji)
        message_ids = []
        for message in messages:
            message_ids.append(message.id)
        unresponded = deepcopy(message_ids)
        if users:
            user_ids = []
            for user in users:
                user_ids.append(user.id)

        reactions = {}
        async def _check_reaction(_, reaction, user):
            if not user.id == self.user.id and reaction.message.id in message_ids:
                emoji = str(reaction.emoji)
                if (not emoji in options) or (users and (not user.id in user_ids)):
                    await self.remove_reaction(reaction.message, emoji, user)
                    return
                unresponded.remove(reaction.message.id)
                if not emoji in reactions:
                    reactions[emoji] = []
                reactions[emoji].append(user)
        handler_id = str(uuid4())
        self.events["on_reaction_add"][handler_id] = [_check_reaction]

        if timeout:
            stop = time() + timeout
        while (not timeout or time() < stop) and unresponded and (not limit or len(messages) - len(unresponded) < limit):
            if len(reactions) > 0 and first:
                if not return_on:
                    break
                else:
                    for reaction in reactions:
                        if reaction in return_on:
                            break
            await asyncio.sleep(self.loop_time)
        del(self.events["on_reaction_add"][handler_id])

        return reactions
