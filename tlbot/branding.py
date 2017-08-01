###############################################################################
#   TransportLayerBot: Branding - All-in-one modular bot for Discord          #
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

NAME_INTERNAL = "TransportLayerBot"     # Changing this is discouraged
NAME_EXTERNAL = "TransportLayerBot"

SOURCE_ORIGIN = "https://github.com/TransportLayer/TLBot-Core"      # Do not change this
SOURCE_CURRENT = "https://github.com/TransportLayer/TLBot-Core"

_AUTHORS = ["TransportLayer"]       # Do not remove people from this list
AUTHORS = _AUTHORS[0]
if len(_AUTHORS) > 1:
    for author in _AUTHORS[1:]:
        AUTHORS += f", {author}"

_LOGO_ICON = [
    "         .::::::.         ",
    "         ::::::::         ",
    "         `::::::`         ",
    "            ::            ",
    "            ::            ",
    "       ..::::::::..       ",
    "     .:``   ::   ``:.     ",
    "    .:      ::      :.    ",
    "   ::       ::       ::   ",
    ".::::::. .::::::. .::::::.",
    ":::::::: :::::::: ::::::::",
    "`::::::` `::::::` `::::::`"
]
_LOGO_TEXT = [      # Size must match _LOGO_ICON
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "  {tag}"
]
LOGO_ICON = _LOGO_ICON[0]
if len(_LOGO_ICON) > 1:
    for line in _LOGO_ICON[1:]:
        LOGO_ICON += f"\n{line}"
LOGO_FULL = f"{_LOGO_ICON[0]}{_LOGO_TEXT[0]}"
if len(_LOGO_ICON) > 1:
    for key in range(len(_LOGO_ICON[1:])):
        key += 1
        LOGO_FULL += f"\n{_LOGO_ICON[key]}{_LOGO_TEXT[key]}"
