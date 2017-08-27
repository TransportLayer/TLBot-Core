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
    def __init__(self, *args, TL_DB, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop_time = 0.5
        self.events = {
            "on_ready": {},
            "on_resumed": {},
            "on_message": {},
            "on_message_noself": {},
            "on_message_nobot": {},
            "on_message_noprivate": {},
            "on_message_noprivate_noself": {},
            "on_message_noprivate_nobot": {},
            "on_message_private": {},
            "on_message_send": {},
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
        self.priority_events = deepcopy(self.events)
        self.user_choices = {}
        self.ext = extender.Extender(self)
        self.ext.load()
        self.cmd = commander.Commander(self)
        self.cmd.hook()
        self.cmd.load()
        self.db = db_tools.BotDatabase(name=TL_DB[2], host=TL_DB[0], port=TL_DB[1])


    # Event Handlers

    async def on_ready(self):
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
        for module in self.priority_events["on_ready"]:
            for function in self.priority_events["on_ready"][module]:
                await function(self)
        # Standard Event Handler
        for module in self.events["on_ready"]:
            for function in self.events["on_ready"][module]:
                await function(self)

    async def on_resumed(self):
        # Priority Event Handler
        for module in self.priority_events["on_resumed"]:
            for function in self.priority_events["on_resumed"][module]:
                await function(self)
        # Standard Event Handler
        for module in self.events["on_resumed"]:
            for function in self.events["on_resumed"][module]:
                await function(self)

    async def on_message(self, message):
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

    async def on_message_delete(self, message):
        # Priority Event Handler
        for module in self.priority_events["on_message_delete"]:
            for function in self.priority_events["on_message_delete"][module]:
                await function(self, message)
        # Standard Event Handler
        for module in self.events["on_message_delete"]:
            for function in self.events["on_message_delete"][module]:
                await function(self, message)

    async def on_message_edit(self, before, after):
        # Priority Event Handler
        for module in self.priority_events["on_message_edit"]:
            for function in self.priority_events["on_message_edit"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_message_edit"]:
            for function in self.events["on_message_edit"][module]:
                await function(self, before, after)

    async def on_reaction_add(self, reaction, user):
        # Priority Event Handler
        for module in self.priority_events["on_reaction_add"]:
            for function in self.priority_events["on_reaction_add"][module]:
                await function(self, reaction, user)
        # Standard Event Handler
        for module in self.events["on_reaction_add"]:
            for function in self.events["on_reaction_add"][module]:
                await function(self, reaction, user)

    async def on_reaction_remove(self, reaction, user):
        # Priority Event Handler
        for module in self.priority_events["on_reaction_remove"]:
            for function in self.priority_events["on_reaction_remove"][module]:
                await function(self, reaction, user)
        # Standard Event Handler
        for module in self.events["on_reaction_remove"]:
            for function in self.events["on_reaction_remove"][module]:
                await function(self, reaction, user)

    async def on_reaction_clear(self, message, reactions):
        # Priority Event Handler
        for module in self.priority_events["on_reaction_clear"]:
            for function in self.priority_events["on_reaction_clear"][module]:
                await function(self, message, reactions)
        # Standard Event Handler
        for module in self.events["on_reaction_clear"]:
            for function in self.events["on_reaction_clear"][module]:
                await function(self, message, reactions)

    async def on_channel_delete(self, channel):
        # Priority Event Handler
        for module in self.priority_events["on_channel_delete"]:
            for function in self.priority_events["on_channel_delete"][module]:
                await function(self, channel)
        # Standard Event Handler
        for module in self.events["on_channel_delete"]:
            for function in self.events["on_channel_delete"][module]:
                await function(self, channel)

    async def on_channel_create(self, channel):
        # Priority Event Handler
        for module in self.priority_events["on_channel_create"]:
            for function in self.priority_events["on_channel_create"][module]:
                await function(self, channel)
        # Standard Event Handler
        for module in self.events["on_channel_create"]:
            for function in self.events["on_channel_create"][module]:
                await function(self, channel)

    async def on_channel_update(self, before, after):
        # Priority Event Handler
        for module in self.priority_events["on_channel_update"]:
            for function in self.priority_events["on_channel_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_channel_update"]:
            for function in self.events["on_channel_update"][module]:
                await function(self, before, after)

    async def on_channel_pins_update(self, channel, last_pin):
        # Priority Event Handler
        for module in self.priority_events["on_channel_pins_update"]:
            for function in self.priority_events["on_channel_pins_update"][module]:
                await function(self, channel, last_pin)
        # Standard Event Handler
        for module in self.events["on_channel_pins_update"]:
            for function in self.events["on_channel_pins_update"][module]:
                await function(self, channel, last_pin)

    async def on_member_join(self, member):
        # Priority Event Handler
        for module in self.priority_events["on_member_join"]:
            for function in self.priority_events["on_member_join"][module]:
                await function(self, member)
        # Standard Event Handler
        for module in self.events["on_member_join"]:
            for function in self.events["on_member_join"][module]:
                await function(self, member)

    async def on_member_remove(self, member):
        # Priority Event Handler
        for module in self.priority_events["on_member_join"]:
            for function in self.priority_events["on_member_join"][module]:
                await function(self, member)
        # Standard Event Handler
        for module in self.events["on_member_join"]:
            for function in self.events["on_member_join"][module]:
                await function(self, member)

    async def on_member_update(self, before, after):
        # Priority Event Handler
        for module in self.priority_events["on_member_update"]:
            for function in self.priority_events["on_member_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_member_update"]:
            for function in self.events["on_member_update"][module]:
                await function(self, before, after)

    async def on_server_join(self, server):
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
        # Priority Event Handler
        for module in self.priority_events["on_server_role_create"]:
            for function in self.priority_events["on_server_role_create"][module]:
                await function(self, role)
        # Standard Event Handler
        for module in self.events["on_server_role_create"]:
            for function in self.events["on_server_role_create"][module]:
                await function(self, role)

    async def on_server_role_delete(self, role):
        # Priority Event Handler
        for module in self.priority_events["on_server_role_delete"]:
            for function in self.priority_events["on_server_role_delete"][module]:
                await function(self, role)
        # Standard Event Handler
        for module in self.events["on_server_role_delete"]:
            for function in self.events["on_server_role_delete"][module]:
                await function(self, role)

    async def on_server_role_update(self, before, after):
        # Priority Event Handler
        for module in self.priority_events["on_server_role_update"]:
            for function in self.priority_events["on_server_role_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_server_role_update"]:
            for function in self.events["on_server_role_update"][module]:
                await function(self, before, after)

    async def on_server_emojis_update(self, before, after):
        # Priority Event Handler
        for module in self.priority_events["on_server_emojis_update"]:
            for function in self.priority_events["on_server_emojis_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_server_emojis_update"]:
            for function in self.events["on_server_emojis_update"][module]:
                await function(self, before, after)

    async def on_server_available(self, server):
        # Priority Event Handler
        for module in self.priority_events["on_server_available"]:
            for function in self.priority_events["on_server_available"][module]:
                await function(self, server)
        # Standard Event Handler
        for module in self.events["on_server_available"]:
            for function in self.events["on_server_available"][module]:
                await function(self, server)

    async def on_server_unavailable(self, server):
        # Priority Event Handler
        for module in self.priority_events["on_server_unavailable"]:
            for function in self.priority_events["on_server_unavailable"][module]:
                await function(self, server)
        # Standard Event Handler
        for module in self.events["on_server_unavailable"]:
            for function in self.events["on_server_unavailable"][module]:
                await function(self, server)

    async def on_voice_state_update(self, before, after):
        # Priority Event Handler
        for module in self.priority_events["on_voice_state_update"]:
            for function in self.priority_events["on_voice_state_update"][module]:
                await function(self, before, after)
        # Standard Event Handler
        for module in self.events["on_voice_state_update"]:
            for function in self.events["on_voice_state_update"][module]:
                await function(self, before, after)

    async def on_member_ban(self, member):
        # Priority Event Handler
        for module in self.priority_events["on_member_ban"]:
            for function in self.priority_events["on_member_ban"][module]:
                await function(self, member)
        # Standard Event Handler
        for module in self.events["on_member_ban"]:
            for function in self.events["on_member_ban"][module]:
                await function(self, member)

    async def on_member_unban(self, server, user):
        # Priority Event Handler
        for module in self.priority_events["on_member_unban"]:
            for function in self.priority_events["on_member_unban"][module]:
                await function(self, server, user)
        # Standard Event Handler
        for module in self.events["on_member_unban"]:
            for function in self.events["on_member_unban"][module]:
                await function(self, server, user)

    async def on_typing(self, channel, user, when):
        # Priority Event Handler
        for module in self.priority_events["on_typing"]:
            for function in self.priority_events["on_typing"][module]:
                await function(self, channel, user, when)
        # Standard Event Handler
        for module in self.events["on_typing"]:
            for function in self.events["on_typing"][module]:
                await function(self, channel, user, when)

    async def on_group_join(self, channel, user):
        # Priority Event Handler
        for module in self.priority_events["on_group_join"]:
            for function in self.priority_events["on_group_join"][module]:
                await function(self, channel, user)
        # Standard Event Handler
        for module in self.events["on_group_join"]:
            for function in self.events["on_group_join"][module]:
                await function(self, channel, user)

    async def on_group_remove(self, channel, user):
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

    async def get_user_role_ids(self, member):
        roles = []
        for role in member.roles:
            roles.append(role.id)
        return roles

    async def get_user_choice(self, destination, *message, options=['✅', '❌'], users=None, timeout=15):
        msg = await self.send_message(destination, *message)
        for reaction in options:
            await self.add_reaction(msg, reaction)
        def _check_reaction(reaction, user):
            if not users:
                if not user == self.user:
                    return True
                else:
                    return False
            else:
                if user in users:
                    return True
                else:
                    return False
        result = await self.wait_for_reaction(options, message=msg, check=_check_reaction, timeout=timeout)
        await self.clear_reactions(msg)
        return msg, result

    async def get_mass_user_choice(self, destinations, *message, options=['✅', '❌'], users=None, timeout=15, first=True, return_on=['✅']):
        sent_messages = []
        for channel in destinations:
            msg = await self.send_message(channel, *message)
            for reaction in options:
                await self.add_reaction(msg, reaction)
            sent_messages.append(msg)
        sent_messages_iter = []
        for msg in sent_messages:
            sent_messages_iter.append(msg.id)
        reactions = []
        async def _check_user_choice(_, reaction, user):
            if reaction.message.id in list(sent_messages_iter):
                if not users:
                    if not user == self.user:
                        reactions.append([reaction, user])
                        sent_messages_iter.remove(msg.id)
                else:
                    if user in users:
                        reactions.append([reaction, user])
                        sent_messages_iter.remove(msg.id)
        handler_id = str(uuid4())
        self.events["on_reaction_add"][handler_id] = [_check_user_choice]
        if timeout:
            stop = time() + timeout
            while time() < stop or not len(sent_messages_iter) == 0:
                if len(reactions) > 0 and first:
                    if len(return_on) == 0:
                        break
                    for reaction in reactions:
                        if reaction[0].emoji in return_on:
                            break
                await asyncio.sleep(self.loop_time)
        else:
            while not len(sent_messages_iter) == 0:
                if len(reactions) > 0 and first:
                    if len(return_on) == 0:
                        break
                    for reaction in reactions:
                        if reaction[0].emoji in return_on:
                            break
                await asyncio.sleep(self.loop_time)
        del(self.events["on_reaction_add"][handler_id])
        return sent_messages, reactions

    async def get_yes_no(self, destination, *message, users=None, timeout=15, on_yes=None, on_no=None, on_timeout=None):
        msg = await self.send_message(destination, *message)
        final = msg
        await self.add_reaction(msg, '✅')
        await self.add_reaction(msg, '❌')
        def _check_reaction(reaction, user):
            if not users:
                if not user == self.user:
                    return True
                else:
                    return False
            else:
                if user in users:
                    return True
                else:
                    return False
        result = await self.wait_for_reaction(['✅', '❌'], message=msg, check=_check_reaction, timeout=timeout)
        if result:
            response = result.reaction.emoji == '✅'
            if response and on_yes:
                if msg.channel.is_private:
                    final = await self.send_message(msg.channel, on_yes)
                    await self.delete_message(msg)
                else:
                    await self.clear_reactions(msg)
                    await self.edit_message(msg, on_yes)
            elif not response and on_no:
                if msg.channel.is_private:
                    final = await self.send_message(msg.channel, on_no)
                    await self.delete_message(msg)
                else:
                    await self.clear_reactions(msg)
                    await self.edit_message(msg, on_no)
            return final, [response, result.user]
        elif on_timeout:
            if msg.channel.is_private:
                final = await self.send_message(msg.channel, on_timeout)
                await self.delete_message(msg)
            else:
                await self.clear_reactions(msg)
                await self.edit_message(msg, on_timeout)
        return final, [None, None]

    async def get_mass_yes_no(self, destinations, *message, users=None, timeout=15, first=True, return_on=True, on_yes=None, on_no=None, on_timeout=None, on_first=None):
        sent_messages = [[], []]
        for channel in destinations:
            msg = await self.send_message(channel, *message)
            await self.add_reaction(msg, '✅')
            await self.add_reaction(msg, '❌')
            sent_messages[0].append(msg)
        sent_messages_iter = []
        for msg in sent_messages[0]:
            sent_messages_iter.append(msg.id)
        responses = []
        async def _check_user_choice(_, reaction, user):
            if reaction.message.id in list(sent_messages_iter):
                if not users:
                    if not user == self.user:
                        sent_messages_iter.remove(msg.id)
                        response = reaction.emoji == '✅'
                        responses.append([response, user])
                        if response and on_yes:
                            if reaction.message.channel.is_private:
                                sent_messages[1].append(await self.send_message(msg.channel, on_yes))
                                sent_messages[0].remove(msg)
                                await self.delete_message(msg)
                            else:
                                await self.clear_reactions(msg)
                                await self.edit_message(msg, on_yes)
                        elif not response and on_no:
                            if reaction.message.channel.is_private:
                                sent_messages[1].append(await self.send_message(msg.channel, on_no))
                                sent_messages[0].remove(msg)
                                await self.delete_message(msg)
                            else:
                                await self.clear_reactions(msg)
                                await self.edit_message(msg, on_no)
                else:
                    if user in users:
                        sent_messages_iter.remove(msg.id)
                        response = reaction.emoji == '✅'
                        responses.append([response, user])
                        if response and on_yes:
                            if reaction.message.channel.is_private:
                                sent_messages[1].append(await self.send_message(msg.channel, on_yes))
                                sent_messages[0].remove(msg)
                                await self.delete_message(msg)
                            else:
                                await self.clear_reactions(msg)
                                await self.edit_message(msg, on_yes)
                        elif not response and on_no:
                            if reaction.message.channel.is_private:
                                sent_messages[1].append(await self.send_message(msg.channel, on_no))
                                sent_messages[0].remove(msg)
                                await self.delete_message(msg)
                            else:
                                await self.clear_reactions(msg)
                                await self.edit_message(msg, on_no)
        handler_id = str(uuid4())
        self.events["on_reaction_add"][handler_id] = [_check_user_choice]
        if timeout:
            stop = time() + timeout
            while not len(sent_messages_iter) == 0:
                if time() >= stop:
                    break
                if len(responses) > 0 and first:
                    if return_on == None:
                        if on_first:
                            for msg in list(sent_messages[0]):
                                if msg.channel.is_private:
                                    sent_messages[1].append(await self.send_message(msg.channel, on_first))
                                    sent_messages[0].remove(msg)
                                    await self.delete_message(msg)
                                else:
                                    await self.clear_reactions(msg)
                                    await self.edit_message(msg, on_first)
                        break
                    else:
                        for response in responses:
                            if response[0] == return_on:
                                if on_first:
                                    for msg in list(sent_messages[0]):
                                        if msg.channel.is_private:
                                            sent_messages[1].append(await self.send_message(msg.channel, on_first))
                                            sent_messages[0].remove(msg)
                                            await self.delete_message(msg)
                                        else:
                                            await self.clear_reactions(msg)
                                            await self.edit_message(msg, on_first)
                                break
                await asyncio.sleep(self.loop_time)
        else:
            while not len(sent_messages_iter) == 0:
                if len(responses) > 0 and first:
                    if return_on == None:
                        if on_first:
                            for msg in list(sent_messages[0]):
                                if msg.channel.is_private:
                                    sent_messages[1].append(await self.send_message(msg.channel, on_first))
                                    sent_messages[0].remove(msg)
                                    await self.delete_message(msg)
                                else:
                                    await self.clear_reactions(msg)
                                    await self.edit_message(msg, on_first)
                        break
                    else:
                        for response in responses:
                            if response[0] == return_on:
                                if on_first:
                                    for msg in list(sent_messages[0]):
                                        if msg.channel.is_private:
                                            sent_messages[1].append(await self.send_message(msg.channel, on_first))
                                            sent_messages[0].remove(msg)
                                            await self.delete_message(msg)
                                        else:
                                            await self.clear_reactions(msg)
                                            await self.edit_message(msg, on_first)
                                break
                await asyncio.sleep(self.loop_time)
        del(self.events["on_reaction_add"][handler_id])
        if timeout and on_timeout and time() >= stop:
            for msg in list(sent_messages[0]):
                if msg.channel.is_private:
                    sent_messages[1].append(await self.send_message(msg.channel, on_timeout))
                    sent_messages[0].remove(msg)
                    await self.delete_message(msg)
                else:
                    await self.clear_reactions(msg)
                    await self.edit_message(msg, on_timeout)
        return sent_messages, responses
