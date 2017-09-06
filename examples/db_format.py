from datetime import datetime

# Database example format

meta = [
    {
        "meta": "info",
        "version": "0.3",
        "created": datetime(2005, 12, 27, 23, 59, 59, 123456)
    },
    {
        "meta": "log",
        "accessed": [
            datetime(2005, 12, 27, 23, 59, 59, 123456),
            datetime(2006, 1, 1, 0, 0, 0, 0),
            datetime(2006, 2, 1, 0, 0, 1, 0)
        ],
        "updated": [
            [
                "0.1",
                "0.2",
                datetime(2005, 12, 28, 12, 54, 3, 5467)
            ],
            [
                "0.2",
                "0.3",
                datetime(2005, 12, 29, 20, 16, 40, 63486)
            ],
        ]
    }
]

servers = [
    {
        "id": "248266453606863597",
        "log": [
            {
                "event": "join",
                "time": datetime(2005, 12, 27, 23, 59, 59, 123456)
            },
            {
                "event": "update_prefix",
                "old": ">",
                "new": "!",
                "by": "184012255391262369"
            }
        ],
        "enabled": True,
        "member": True,
        "joinable": True,
        "banned": False,
        "prefix": "!"
    }
]

commands = [
    {
        "owner": "248266453606863597",
        "public": False,
        "available": [
            "248266453606863597"
        ],
        "enable_all": False,
        "enabled": [
            "248266453606863597"
        ],
        "name": "hello",
        "use_permissions": True,
        # "permissions": 4,     # Requires 4: Full Access
        # "permissions": 3,     # Requires 3: Run All, Create/Delete 2 (Server Management)
        # "permissions": 2,     # Requires 2: Run Most, Create/Delete 1 (Ban)
        # "permissions": 1,     # Requires 1: Run Some (Kick)
        "permissions": 0,       # Requires 0: Default Access
        "use_roles": True,
        "roles": [
            "237862168886556694"
        ],
        "action": "reply",
        "message": "Hello!"
    }
]

roles = [
    {
        "owner": "248266453606863597",
        "id": "237862168886556694",
        "children": [
            "256782567365291440"
        ],
        "permission": 4,
        "open": False,
        "joinable": [
            "250132786465546840"
        ]
    }
]

events = [
    {
        "owner": "248266453606863597",
        "public": False,
        "available": [
            "248266453606863597"
        ],
        "enable_all": False,
        "enabled": [
            "248266453606863597"
        ],
        "name": "welcome",
        "event": "on_member_join",
        "action": "reply",
        "channel": "258554880867878312",
        "message": "Welcome to the server, $USER!"
    }
]

users = [
    {
        "id": "184012255391262369",
        "superuser": True,
        "banned": False,
        "support": True,
        "support_level": 3      # 1, 2, or 3 (2 allows remote execution, 3 allows joining server)
    }
]

plugin_message_filter = [
    {
        "owner": "248266453606863597",
        "enabled": True,
        "words": [
            "fuit",
            "shck"
        ]
    }
]
