###############################################################################
#   TransportLayerBot: Database Utils - All-in-one modular bot for Discord    #
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
from pymongo import MongoClient
from datetime import datetime

log = logger.get_logger(__name__)

class TLBotDB:
    def __init__(self, name="TransportLayerBot", host="127.0.0.1", port=27017):
        log.info("Connecting to database {} at {}:{}".format(name, host, port))
        mongo = MongoClient(host=host, port=port)
        self.db = mongo[name]

        db_meta = self.db.meta.find({"meta": "times"})
        if db_meta.count():
            log.info("Database created {}".format(db_meta[0]["created"]))
        else:
            log.warn("Database not found; creating new database")
            self.db.meta.insert_one(
                {
                    "meta": "times",
                    "created": datetime.now()
                }
            )

    def check_exists(self, collection, *args):
        db_query = self.db[collection].find(*args)
        return db_query.count()

    # Servers
    def server_create(self, server_id):
        if not self.check_exists("servers", {"id": server_id}):
            self.db.servers.insert_one(
                {
                    "id": server_id,
                    "added": datetime.now(),
                    "settings": {
                        "prefix": '!'
                    },
                    "enabled": True,
                    "orphaned": False
                }
            )
            return True, None
        else:
            return False, "server already exists"

    def server_delete(self, server):
        if isinstance(server, str):
            server = {"id": server}
        if self.check_exists("servers", server):
            self.db.servers.delete_many(server)
            for collection in self.db.collection_names():
                self.db[collection].delete_many({"owner": server["id"]})
            return True, None
        else:
            return False, "server not found"

    def server_get(self, server):
        if isinstance(server, str):
            server = {"id": server}
        server = self.db.servers.find(server)
        if server.count():
            return server[0], None
        else:
            return False, "server not found"

    def server_get_all_ids(self):
        ids = []
        all_servers = self.db.servers.find({})
        for server in all_servers:
            ids.append(server["id"])
        return ids

    def server_settings(self, server):
        if isinstance(server, str):
            server = {"id": server}
        server, e = self.server_get(server)
        if server:
            return server["settings"], None
        else:
            return False, e

    def server_set(self, server, setting, value):
        if isinstance(server, str):
            server = {"id": server}
        server, e = self.server_get(server)
        if server:
            self.db.servers.update_many(server, {
                "$set": {"settings.{}".format(setting): value}
            })
            return True, None
        else:
            return False, e

    def server_enabled(self, server):
        if isinstance(server, str):
            server = {"id": server}
        server, e = self.server_get(server)
        if server:
            return server["enabled"], None
        else:
            return False, e

    def server_orphaned(self, server):
        if isinstance(server, str):
            server = {"id": server}
        server, e = self.server_get(server)
        if server:
            return server["orphaned"], None
        else:
            return False, e

    def server_enable(self, server, enable=True):
        if isinstance(server, str):
            server = {"id": server}
        server, e = self.server_get(server)
        if server:
            self.db.servers.update_many(server, {
                "$set": {"enabled": enable}
            })
            return True, None
        else:
            return False, e

    def server_orphan(self, server, orphan=True):
        if isinstance(server, str):
            server = {"id": server}
        server, e = self.server_get(server)
        if server:
            self.db.servers.update_many(server, {
                "$set": {"orphaned": orphan}
            })
            return True, None
        else:
            return False, e

    # Commands
    def command_create(self, server_id, command_name, command_type, command=None):
        if self.check_exists("servers", {"id": server_id}):
            if not self.check_exists("commands", {"owner": server_id, "name": command_name}):
                if command_type in ("module"):
                    self.db.commands.insert_one(
                        {
                            "owner": server_id,
                            "name": command_name,
                            "added": datetime.now(),
                            "type": command_type,
                            "command": command,
                            "enabled": True
                        }
                    )
                    return True, None
                else:
                    return False, "command already exists"
        else:
            return False, "server not found"

    def command_delete(self, command, server_id=None):
        if isinstance(command, str):
            command = {"owner": server_id, "name": command}
        if self.check_exists("servers", {"id": command["owner"]}):
            if self.check_exists("commands", command):
                self.db.commands.delete_many(command)
                return True, None
            else:
                return False, "command not found"
        else:
            return False, "server not found"

    def command_get(self, command, server_id=None):
        if isinstance(command, str):
            command = {"owner": server_id, "name": command}
        command = self.db.commands.find(command)
        if command.count():
            return command[0], None
        else:
            return False, "command not found"

    def command_get_all_names(self, server_id):
        names = []
        all_commands = self.db.commands.find({"owner": server_id})
        for command in all_commands:
            names.append(command["name"])
        return names

    def command_set(self, command, server_id, new_command):
        if isinstance(command, str):
            command = {"owner": server_id, "name": command}
        command, e = self.command_get(command)
        if command:
            self.db.commands.update_many(command, {
                "$set": {"command": new_command}
            })
            return True, None
        else:
            return False, e

    def command_rename(self, command, server_id, name):
        if isinstance(command, str):
            command = {"owner": server_id, "name": command}
        command, e = self.command_get(command)
        if command:
            if not self.check_exists("commands", {"owner": server_id, "name": name}):
                self.db.commands.update_many(command, {
                    "$set": {"name": name}
                })
                return True, None
            else:
                return False, "command already exists"
        else:
            return False, e

    def command_enabled(self, command, server_id=None):
        if isinstance(command, str):
            command = {"owner": server_id, "name": command}
        command, e = self.command_get(command)
        if command:
            return command["enabled"], None
        else:
            return False, e

    def command_enable(self, command, server_id=None, enable=True):
        if isinstance(command, str):
            command = {"owner": server_id, "name": command}
        command, e = self.command_get(command)
        if command:
            self.db.commands.update_many(command, {
                "$set": {"enabled": enable}
            })
            return True, None
        else:
            return False, e

    # Events
    def event_create(self, server_id, event_type, command, channel=None):
        if self.check_exists("servers", {"id": server_id}):
            if not self.check_exists("events", {"owner": server_id, "event": event_type, "command": command, "channel": channel}):
                if event_type in ("join", "leave"):
                    self.db.events.insert_one(
                        {
                            "owner": server_id,
                            "event": event_type,
                            "added": datetime.now(),
                            "command": command,
                            "channel": channel,
                            "enabled": True
                        }
                    )
                    return True, None
            else:
                return False, "event already exists"
        else:
            return False, "server not found"

    def event_delete(self, event):
        if self.check_exists("events", event):
            self.db.events.delete_many(event)
            return True, None
        else:
            return False, "event not found"

    def event_get(self, event):
        event = self.db.events.find(event)
        if event.count():
            return event[0], None
        else:
            return False, "event not found"

    def event_get_all(self, server_id):
        events = []
        all_events = self.db.events.find({"owner": server_id})
        for event in all_events:
            events.append(event)
        return events

    def event_set(self, event, command):
        event, e = self.event_get(event)
        if event:
            if not self.check_exists("events", {"owner": event["owner"], "event": event["event"], "command": command, "channel": event["channel"]}):
                self.db.events.update_many(event, {
                    "$set": {"command": command}
                })
                return True, None
            else:
                return False, "event already exists"
        else:
            return False, e

    def event_move(self, event, channel):
        event, e = self.event_get(event)
        if event:
            if not self.check_exists("events", {"owner": event["owner"], "event": event["event"], "command": event["command"], "channel": channel}):
                self.db.events.update_many(event, {
                    "$set": {"channel": channel}
                })
                return True, None
            else:
                return False, "event already exists"
        else:
            return False, e

    def event_enabled(self, event):
        event, e = self.event_get(event)
        if event:
            return event["enabled"], None
        else:
            return False, e

    def event_enable(self, event, enable=True):
        event, e = self.event_get(event)
        if event:
            self.db.events.update_many(event, {
                "$set": {"enabled": enable}
            })
            return True, None
        else:
            return False, e
