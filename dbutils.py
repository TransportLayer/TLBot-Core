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

    def add_server(self, server_id):
        if not self.check_exists("servers", {"id": server_id}):
            self.db.servers.insert_one(
                {
                    "id": server_id,
                    "added": datetime.now(),
                    "admins": [],
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

    def remove_server(self, server_id):
        if self.check_exists("servers", {"id": server_id}):
            self.db.servers.delete_many({"id": server_id})
            return True, None
        else:
            return False, "server does not exist"

    def get_server(self, server_id):
        server = self.db.servers.find({"id": server_id})
        if server.count():
            return server[0], None
        else:
            return False, "server not found"

    def get_all_server_ids(self):
        ids = []
        all_servers = self.db.servers.find({})
        for server in all_servers:
            ids.append(server["id"])
        return ids

    def add_command(self, server_id, command_name, command_type, command=None):
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
                            "runnable": [],
                            "enabled": True
                        }
                    )
                    return True, None
                else:
                    return False, "command already exists"
        else:
            return False, "server not found"

    def get_command(self, server_id, command):
        command = self.db.commands.find({"owner": server_id, "name": command})
        if command.count():
            return command[0], None
        else:
            return False, "command not found"
