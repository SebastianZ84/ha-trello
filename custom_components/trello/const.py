"""Constants for the trello integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Final

DOMAIN: Final = "trello"

LOGGER = logging.getLogger(__package__)

CONF_USER_ID = "user_id"
CONF_USER_EMAIL = "user_email"
CONF_BOARD_IDS = "board_ids"
CONF_UPDATE_INTERVAL = "update_interval"

# Default update interval in seconds
DEFAULT_UPDATE_INTERVAL = 1


@dataclass
class Board:
    """A Trello board."""

    id: str
    name: str
    lists: dict[str, List]


@dataclass
class Card:
    """A Trello card."""

    id: str
    name: str
    desc: str
    due: str | None = None
    list_id: str = ""


@dataclass
class List:
    """A Trello list."""

    id: str
    name: str
    card_count: int
    cards: list[Card]
