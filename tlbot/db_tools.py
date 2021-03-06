###############################################################################
#   TransportLayerBot: Database Tools - All-in-one modular bot for Discord    #
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
from tlbot import lang

log = logger.get_logger(__name__)

DB_VERSION = "0.1"

class BotDatabase:
    def __init__(self, name="TransportLayerBot", host="127.0.0.1", port=27017):
        log.info(f"Connecting to database {name} at {host}:{port}")
        mongo = MongoClient(host=host, port=port)
        self._db = mongo[name]
        db_info = self._db.meta.find({"meta": "info"})
        if db_info.count():
            log.info(f"Database created {db_info[0]['created']}")
        else:
            log.warn("Creating new database")
            self._db.meta.insert_one(
                {
                    "meta": "info",
                    "version": DB_VERSION,
                    "created": datetime.utcnow()
                }
            )
            self._db.meta.insert_one(
                {
                    "meta": "log",
                    "accessed": [],
                    "updated": []
                }
            )
        self._db.meta.update_one(
            {"meta": "log"}, {
                "$addToSet": {
                    "accessed": datetime.utcnow()
                }
            }
        )

    async def check_exists(self, collection, *args):
        db_query = self._db[collection].find(*args)
        return db_query.count()


    # Servers

    async def server_join(self, server_id):
        if not await self.check_exists("servers", {"id": server_id}):
            self._db.servers.insert_one(
                {
                    "id": server_id,
                    "log": [],
                    "enabled": True,
                    "member": True,
                    "joinable": True,
                    "banned": False,
                    "prefix": '!'
                }
            )
        self._db.servers.update_one(
            {"id": server_id}, {
                "$set": {
                    "enabled": True,
                    "member": True
                },
                "$addToSet": {
                    "log": {
                        "event": "join",
                        "time": datetime.utcnow()
                    }
                }
            }
        )
        return True

    async def server_leave(self, server_id):
        if await self.check_exists("servers", {"id": server_id}):
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$set": {
                        "enabled": False,
                        "member": False
                    },
                    "$addToSet": {
                        "log": {
                            "event": "leave",
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.SRV_NOT_FOUND

    async def server_get(self, server_id, attribute):
        if await self.check_exists("servers", {"id": server_id}):
            server = self._db.servers.find({"id": server_id})
            return server[0][attribute], None
        else:
            return False, lang.SRV_NOT_FOUND

    async def server_get_ids(self, query):
        ids = []
        for server in self._db.servers.find(query):
            ids.append(server["id"])
        return ids

    async def server_enable(self, server_id, enable=True, by=None, reason=None):
        if await self.check_exists("servers", {"id": server_id}):
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$set": {
                        "enabled": enable
                    },
                    "$addToSet": {
                        "log": {
                            "event": "enable" if enable else "disable",
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.SRV_NOT_FOUND

    async def server_member(self, server_id, member=True, by=None, reason=None):
        if await self.check_exists("servers", {"id": server_id}):
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$set": {
                        "member": member
                    },
                    "$addToSet": {
                        "log": {
                            "event": "is_member" if member else "not_member",
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.SRV_NOT_FOUND

    async def server_joinable(self, server_id, joinable=True, by=None, reason=None):
        if await self.check_exists("servers", {"id": server_id}):
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$set": {
                        "joinable": joinable
                    },
                    "$addToSet": {
                        "log": {
                            "event": "joinable" if joinable else "unjoinable",
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.SRV_NOT_FOUND

    async def server_ban(self, server_id, ban=True, by=None, reason=None):
        if await self.check_exists("servers", {"id": server_id}):
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$set": {
                        "banned": ban
                    },
                    "$addToSet": {
                        "log": {
                            "event": "ban" if ban else "unban",
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.SRV_NOT_FOUND

    async def server_set_prefix(self, server_id, new_prefix, by=None, reason=None):
        if await self.check_exists("servers", {"id": server_id}):
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$set": {
                        "prefix": new_prefix
                    },
                    "$addToSet": {
                        "log": {
                            "event": "update_prefix",
                            "old": await self.server_get(server_id, "prefix"),
                            "new": new_prefix,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.SRV_NOT_FOUND


    # Commands

    async def command_add(self, server_id, public, available_for, enable_all, enabled_for, name, use_permissions, permissions, use_roles, roles, action, by=None, reason=None, **kwargs):
        if not await self.check_exists("commands", {"owner": server_id, "name": name}):
            document = {
                "owner": server_id,
                "public": public,
                "available": available_for,
                "enable_all": enable_all,
                "enabled": enabled_for,
                "name": name,
                "use_permissions": use_permissions,
                "permissions": permissions,
                "use_roles": use_roles,
                "roles": roles,
                "action": action,
            }
            document.update(kwargs)
            self._db.commands.insert_one(document)
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "command_create",
                            "command": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.CMD_EXISTS

    async def command_remove(self, server_id, name, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            self._db.commands.delete_one({"owner": server_id, "name": name})
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "command_delete",
                            "command": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.CMD_NOT_FOUND

    async def command_find(self, name, server_id=None):
        if server_id:
            return self._db.commands.find({"name": name, "enabled": server_id})
        else:
            return self._db.commands.find({"name": name})

    async def command_public(self, server_id, name, public=True, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            self._db.commands.update_one(
                {"owner": server_id, "name": name}, {
                    "$set": {
                        "public": public
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "command_public" if enable else "command_private",
                            "command": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.CMD_NOT_FOUND

    async def command_available(self, server_id, name, available_for, available=True, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            if available:
                self._db.commands.update_one(
                    {"owner": server_id, "name": name}, {
                        "$addToSet": {
                            "available": available_for,
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "command_available_for_server",
                                "command": name,
                                "server": available_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
            else:
                self._db.commands.update_one(
                    {"owner": server_id, "name": name}, {
                        "$pull": {
                            "available": available_for
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "command_unavailable_for_server",
                                "command": name,
                                "server": available_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
        else:
            return False, lang.CMD_NOT_FOUND

    async def command_enable_all(self, server_id, name, enable_all=True, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            self._db.commands.update_one(
                {"owner": server_id, "name": name}, {
                    "$set": {
                        "enable_all": enable_all
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "command_enable_all" if enable else "command_unenable_all",
                            "command": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.CMD_NOT_FOUND

    async def command_enable(self, server_id, name, enable_for, enable=True, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            if enable:
                self._db.commands.update_one(
                    {"owner": server_id, "name": name}, {
                        "$addToSet": {
                            "enabled": enable_for,
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "command_enable_for_server",
                                "command": name,
                                "server": enable_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
            else:
                self._db.commands.update_one(
                    {"owner": server_id, "name": name}, {
                        "$pull": {
                            "enabled": enable_for
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "command_disable_for_server",
                                "command": name,
                                "server": enable_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
        else:
            return False, lang.CMD_NOT_FOUND

    async def command_use_permissions(self, server_id, name, use_permissions=True, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            self._db.commands.update_one(
                {"owner": server_id, "name": name}, {
                    "$set": {
                        "use_permissions": use_permissions
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "command_use_permissions" if enable else "command_disable_permissions",
                            "command": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.CMD_NOT_FOUND

    async def command_set_permissions(self, server_id, name, permissions, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            self._db.commands.update_one(
                {"owner": server_id, "name": name}, {
                    "$set": {
                        "permissions": permissions
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "command_set_permissions",
                            "command": name,
                            "permissions": permissions,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.CMD_NOT_FOUND

    async def command_use_roles(self, server_id, name, use_roles=True, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            self._db.commands.update_one(
                {"owner": server_id, "name": name}, {
                    "$set": {
                        "use_roles": use_roles
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "command_use_roles" if enable else "command_disable_roles",
                            "command": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.CMD_NOT_FOUND

    async def command_role(self, server_id, name, role, add=True, by=None, reason=None):
        if await self.check_exists("commands", {"owner": server_id, "name": name}):
            if add:
                self._db.commands.update_one(
                    {"owner": server_id, "name": name}, {
                        "$addToSet": {
                            "roles": role,
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "command_add_role",
                                "command": name,
                                "role": role,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
            else:
                self._db.commands.update_one(
                    {"owner": server_id, "name": name}, {
                        "$pull": {
                            "roles": roll
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "command_remove_role",
                                "command": name,
                                "role": role,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
        else:
            return False, lang.CMD_NOT_FOUND


    # Roles

    async def role_add(self, server_id, role_id, children, permission, is_open, joinable_by, by=None, reason=None):
        if not await self.check_exists("roles", {"owner": server_id, "id": role_id}):
            self._db.roles.insert_one(
                {
                    "owner": server_id,
                    "id": role_id,
                    "children": children,
                    "permission": permission,
                    "open": is_open,
                    "joinable": joinable_by
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "role_create",
                            "role": role_id,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.ROLE_EXISTS

    async def role_remove(self, server_id, role_id, by=None, reason=None):
        if await self.check_exists("roles", {"owner": server_id, "id": role_id}):
            self._db.roles.delete_one({"owner": server_id, "id": role_id})
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "role_delete",
                            "role": role_id,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.ROLE_NOT_FOUND

    async def role_find(self, role_id):
        return self._db.roles.find({"id": role_id})

    async def role_child(self, server_id, role_id, child_id, add=True, by=None, reason=None):
        if await self.check_exists("roles", {"owner": server_id, "id": role_id}):
            if add:
                self._db.roles.update_one(
                    {"owner": server_id, "id": role_id}, {
                        "$addToSet": {
                            "children": role_id,
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "role_add_child",
                                "role": role_id,
                                "child": child_id,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
            else:
                self._db.roles.update_one(
                    {"owner": server_id, "id": role_id}, {
                        "$pull": {
                            "children": child_id
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "role_remove_child",
                                "role": role_id,
                                "child": child_id,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
        else:
            return False, lang.ROLE_NOT_FOUND

    async def role_set_permission(self, server_id, role_id, permission, by=None, reason=None):
        if await self.check_exists("roles", {"owner": server_id, "id": role_id}):
            self._db.roles.update_one(
                {"owner": server_id, "id": role_id}, {
                    "$set": {
                        "permission": permission
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "role_set_permission",
                            "role": role_id,
                            "permission": permission,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.ROLE_NOT_FOUND

    async def role_open(self, server_id, role_id, is_open=True, by=None, reason=None):
        if await self.check_exists("roles", {"owner": server_id, "id": role_id}):
            self._db.roles.update_one(
                {"owner": server_id, "id": role_id}, {
                    "$set": {
                        "open": is_open
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "role_open" if is_open else "role_close",
                            "role": role_id,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.ROLE_NOT_FOUND

    async def role_joinable(self, server_id, role_id, joinable_for, joinable=True, by=None, reason=None):
        if await self.check_exists("roles", {"owner": server_id, "id": role_id}):
            if joinable:
                self._db.roles.update_one(
                    {"owner": server_id, "id": role_id}, {
                        "$addToSet": {
                            "joinable": joinable_for,
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "role_joinable",
                                "role": role_id,
                                "joinable_by": joinable_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
            else:
                self._db.roles.update_one(
                    {"owner": server_id, "id": role_id}, {
                        "$pull": {
                            "joinable": joinable_for
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "role_unjoinable",
                                "role": role_id,
                                "unjoinable_by": joinable_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
        else:
            return False, lang.ROLE_NOT_FOUND


    # Events

    async def event_add(self, server_id, public, available_for, enable_all, enabled_for, name, event, action, by=None, reason=None, **kwargs):
        if not await self.check_exists("events", {"owner": server_id, "name": name}):
            document = {
                "owner": server_id,
                "public": public,
                "available": available_for,
                "enable_all": enable_all,
                "enabled": enabled_for,
                "name": name,
                "event": event,
                "action": action
            }
            document.update(kwargs)
            self._db.events.insert_one(document)
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "event_create",
                            "event_name": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.EVENT_EXISTS

    async def event_remove(self, server_id, name, by=None, reason=None):
        if await self.check_exists("events", {"owner": server_id, "name": name}):
            self._db.events.delete_one({"owner": server_id, "name": name})
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "event_delete",
                            "event_name": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.EVENT_NOT_FOUND

    async def event_find(self, name, server_id=None):
        if server_id:
            return self._db.events.find({"name": name, "enabled": server_id})
        else:
            return self._db.events.find({"name": name})

    async def event_get(self, event, server_id=None):
        if server_id:
            return self._db.events.find({"event": event, "enabled": server_id})
        else:
            return self._db.events.find({"event": event})

    async def event_public(self, server_id, name, public=True, by=None, reason=None):
        if await self.check_exists("events", {"owner": server_id, "name": name}):
            self._db.events.update_one(
                {"owner": server_id, "name": name}, {
                    "$set": {
                        "public": public
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "event_public" if enable else "event_private",
                            "event_name": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.EVENT_NOT_FOUND

    async def event_available(self, server_id, name, available_for, available=True, by=None, reason=None):
        if await self.check_exists("events", {"owner": server_id, "name": name}):
            if available:
                self._db.events.update_one(
                    {"owner": server_id, "name": name}, {
                        "$addToSet": {
                            "available": available_for,
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "event_available_for_server",
                                "event_name": name,
                                "server": available_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
            else:
                self._db.events.update_one(
                    {"owner": server_id, "name": name}, {
                        "$pull": {
                            "available": available_for
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "event_unavailable_for_server",
                                "event_name": name,
                                "server": available_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
        else:
            return False, lang.EVENT_NOT_FOUND

    async def event_enable_all(self, server_id, name, enable_all=True, by=None, reason=None):
        if await self.check_exists("events", {"owner": server_id, "name": name}):
            self._db.events.update_one(
                {"owner": server_id, "name": name}, {
                    "$set": {
                        "enable_all": enable_all
                    }
                }
            )
            self._db.servers.update_one(
                {"id": server_id}, {
                    "$addToSet": {
                        "log": {
                            "event": "event_enable_all" if enable else "event_unenable_all",
                            "event_name": name,
                            "by": by,
                            "reason": reason,
                            "time": datetime.utcnow()
                        }
                    }
                }
            )
            return True, None
        else:
            return False, lang.EVENT_NOT_FOUND

    async def event_enable(self, server_id, name, enable_for, enable=True, by=None, reason=None):
        if await self.check_exists("events", {"owner": server_id, "name": name}):
            if enable:
                self._db.events.update_one(
                    {"owner": server_id, "name": name}, {
                        "$addToSet": {
                            "enabled": enable_for,
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "event_enable_for_server",
                                "event_name": name,
                                "server": enable_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
            else:
                self._db.events.update_one(
                    {"owner": server_id, "name": name}, {
                        "$pull": {
                            "enabled": enable_for
                        }
                    }
                )
                self._db.servers.update_one(
                    {"id": server_id}, {
                        "$addToSet": {
                            "log": {
                                "event": "event_disable_for_server",
                                "event_name": name,
                                "server": enable_for,
                                "by": by,
                                "reason": reason,
                                "time": datetime.utcnow()
                            }
                        }
                    }
                )
                return True, None
        else:
            return False, lang.EVENT_NOT_FOUND


    # Users

    async def user_find(self, query):
        return self._db.users.find(query)

    async def user_find_ids(self, query):
        ids = []
        for user in await self.user_find(query):
            ids.append(user["id"])
        return ids


    # General

    async def get_user_permissions(self, user_id, role_ids):
        highest_permission = 0
        for role_id in role_ids:
            for role in await self.role_find(role_id):
                if role["permission"] > highest_permission:
                    highest_permission = role["permission"]
        is_superuser = False
        for user in await self.user_find({"id": user_id}):
            is_superuser = user["superuser"]
        return [highest_permission, is_superuser]
