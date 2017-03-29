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
from TLLogger import logger
import textutils

log = logger.get_logger(__name__)

class TransportLayerBot(discord.Client):
    async def on_ready(self):
        log.info("Logged in as {}#{} (ID: {})".format(self.user.name, self.user.discriminator, self.user.id))

    async def on_resumed(self):
        log.info("Successfully resumed session")

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

        await self.send_message(channel, message)

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

    async def on_message(self, message):
            await self.receive_logged_message(message)