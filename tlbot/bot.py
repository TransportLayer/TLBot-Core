###############################################################################
#   TransportLayerBot: Bot - All-in-one modular bot for Discord               #
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

import asyncio
import discord
from time import time
from TLLogger import logger
from tlbot import textutils
from tlbot.db import tools as dbtools
from tlbot import commander

log = logger.get_logger(__name__)

class TransportLayerBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = dbtools.TLBotDB(**kwargs["DB_INFO"])
        self.interpretor = commander.Interpretor(self)
        self.interpretor.init_commands_in_all_servers()
        self.send_queue = []
        self.send_log = {}
        self.blocking = {}

    async def init_dm(self, channel):
        if channel.is_private:
            ok, e = self.db.server_create(channel.id, True)
            if ok:
                self.interpretor.init_commands(channel.id)
                log.info("Opened DM {}".format(channel.name if channel.type == discord.ChannelType.group else channel.recipients[0].name))

    async def init_server_documents(self, server):
        if isinstance(server, str):
            server = discord.utils.get(self.servers, id=server)
        log.info("Joined server {}".format(server.name))
        ok, e = self.db.server_create(server.id)
        self.interpretor.init_commands(server.id)
        if not ok:
            log.warn("Could not add server {} to database: {}".format(server.name, e))

    async def delete_server_documents(self, server):
        if isinstance(server, str):
            server = discord.utils.get(self.servers, id=server)
        log.info("Left server {}".format(server.name))
        ok, e = self.db.server_delete(server.id)
        if not ok:
            log.warn("Could not remove server {} from database: {}".format(server.name, e))

    async def clean_send_log(self, max_time=300):
        removed = 0
        for track_id in self.send_log:
            for record in self.send_log[track_id]:
                if record < time() - max_time:
                    self.send_log[track_id].remove(record)
                    removed += 1
        return removed

    async def check_rate(self, ids, track_time=300):
        count = 0
        if isinstance(ids, str):
            ids = [ids]
        for track_id in ids:
            if track_id in self.send_log:
                for record in self.send_log[track_id]:
                    if record >= time() - track_time:
                        count += 1
        return count / track_time

    async def queue_add(self, out_type, track_id, *args):
        if track_id:
            if not track_id in self.send_log:
                self.send_log[track_id] = []
            self.send_log[track_id].append(time())
        self.send_queue.append((out_type, *args))
        if await self.check_rate(track_id, 1) > self.db.setting_get_channel_cap()[0]:
            self.blocking[track_id] = time()

    async def send_logged_message(self, channel, message):
        log_string = textutils.TEMPLATES["send"]
        if channel.is_private:
            if channel.type == discord.ChannelType.group:
                log_string = log_string.format("(DM)", channel.name, textutils.safe_string(message))
            else:
                log_string = log_string.format("(DM)", channel.recipients[0].name, textutils.safe_string(message))
        else:
            log_string = log_string.format(channel.server.name, "#{}".format(channel.name), textutils.safe_string(message))
        log.info(log_string)
        await super().send_message(channel, message)

    async def send_message(self, channel, message, ignore_queue=False):
        if not ignore_queue:
            await self.queue_add("message", channel.id, channel, message)
        else:
            await self.send_logged_message(channel, message)

    async def receive_logged_message(self, message):
        log_string = textutils.TEMPLATES["receive"]
        if message.channel.is_private:
            if message.channel.type == discord.ChannelType.group:
                log_string = log_string.format("(DM)", message.channel.name, message.author.name, textutils.safe_string(message.content))
            else:
                log_string = log_string.format("(DM)", message.channel.recipients[0].name, message.author.name, textutils.safe_string(message.content))
        else:
            log_string = log_string.format(message.server.name, "#{}".format(message.channel.name), message.author.name, textutils.safe_string(message.content))
        log.info(log_string)

    async def verify_servers(self):
        real_servers = []
        db_servers = self.db.server_get_all_ids()
        for server in self.servers:
            real_servers.append(server.id)
        for server in db_servers:
            if not server in real_servers and not self.db.server_dm(server)[0] and not self.db.server_orphaned(server)[0]:
                log.warn("Found orphaned server document with ID {}".format(server))
                ok, e = self.db.server_orphan(server)
                if not ok:
                    log.warn("Could not orphan server {}: {}".format(server, e))
        for server in real_servers:
            if not server in db_servers:
                log.warn("Found server missing documents with ID {}".format(server))
                await self.init_server_documents(server)
            elif self.db.server_orphaned(server)[0]:
                log.warn("Found server matching orphaned document with ID {}".format(server))
                ok, e = self.db.server_orphan(server, False)
                if not ok:
                    log.warn("Could not unorphan server {}: {}".format(server, e))

    async def run_send_limiter(self):
        next_warn = 0
        while self.is_logged_in and not self.is_closed:
            if self.send_queue:
                if len(self.send_queue) >= 30 and not next_warn:
                    log.warn("The send queue contains {} requests".format(len(self.send_queue)))
                    next_warn = 16
                outgoing = self.send_queue.pop(0)
                if outgoing[0] == "message":
                    await self.send_logged_message(*outgoing[1:])
                else:
                    log.warn("Invalid item in send queue of type {}".format(outgoing[0]))
                if next_warn:
                    next_warn -= 1
            await self.clean_send_log()
            for track_id, timestamp in list(self.blocking.items()):
                if timestamp < time() - 3:
                    del(self.blocking[track_id])
            await asyncio.sleep(1 / self.db.setting_get_global_rate()[0])

    async def on_ready(self):
        log.info("Logged in as {}#{} (ID: {})".format(self.user.name, self.user.discriminator, self.user.id))
        await self.verify_servers()
        await self.run_send_limiter()

    async def on_resumed(self):
        log.info("Successfully resumed session")

    async def on_server_join(self, server):
        await self.init_server_documents(server)

    async def on_server_remove(self, server):
        await self.delete_server_documents(server)

    async def on_message(self, message):
        if not message.author == self.user:
            await self.receive_logged_message(message)
        if not message.author.bot and not message.channel.id in self.blocking:
            await self.init_dm(message.channel)
            await self.interpretor.interpret(message)
