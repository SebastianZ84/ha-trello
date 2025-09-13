"""The Trello integration."""
from __future__ import annotations

from trello import Member, TrelloClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_API_TOKEN, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.components.frontend import add_extra_js_url
import voluptuous as vol

from .const import CONF_BOARD_IDS, DOMAIN
from .coordinator import TrelloDataUpdateCoordinator

PLATFORMS: list[str] = [Platform.SENSOR]

# Service schemas
MOVE_CARD_SERVICE_SCHEMA = vol.Schema({
    vol.Required("card_id"): cv.string,
    vol.Required("target_list_id"): cv.string,
})

CREATE_CARD_SERVICE_SCHEMA = vol.Schema({
    vol.Required("list_id"): cv.string,
    vol.Required("name"): cv.string,
    vol.Optional("description", default=""): cv.string,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    config_boards = entry.options[CONF_BOARD_IDS]
    config_data = entry.data
    trello_client = TrelloClient(
        api_key=config_data[CONF_API_KEY],
        api_secret=config_data[CONF_API_TOKEN],
    )
    trello_coordinator = TrelloDataUpdateCoordinator(hass, trello_client, config_boards)
    await trello_coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = trello_coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_entry))

    # Register services
    async def async_move_card(call: ServiceCall) -> None:
        """Move a card to a different list."""
        card_id = call.data["card_id"]
        target_list_id = call.data["target_list_id"]
        
        await hass.async_add_executor_job(
            _move_card_sync, trello_client, card_id, target_list_id
        )
        await trello_coordinator.async_request_refresh()

    async def async_create_card(call: ServiceCall) -> None:
        """Create a new card in a list."""
        list_id = call.data["list_id"]
        name = call.data["name"] 
        description = call.data.get("description", "")
        
        await hass.async_add_executor_job(
            _create_card_sync, trello_client, list_id, name, description
        )
        await trello_coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, "move_card", async_move_card, schema=MOVE_CARD_SERVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "create_card", async_create_card, schema=CREATE_CARD_SERVICE_SCHEMA
    )

    # Register frontend resources (HACS will handle www files automatically)
    add_extra_js_url(hass, "/local/community/trello_enhanced/trello-board-card.js")
    add_extra_js_url(hass, "/local/community/trello_enhanced/trello-board-card-editor.js")

    return True


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update a given config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _move_card_sync(client: TrelloClient, card_id: str, target_list_id: str) -> None:
    """Move card synchronously."""
    card = client.get_card(card_id)
    target_list = client.get_list(target_list_id)
    card.change_list(target_list.id)


def _create_card_sync(client: TrelloClient, list_id: str, name: str, description: str) -> None:
    """Create card synchronously."""
    target_list = client.get_list(list_id)
    target_list.add_card(name, desc=description)


class TrelloAdapter:
    """Adapter for Trello lib's client."""

    def __init__(self, client: TrelloClient) -> None:
        """Initialize with Trello lib client."""
        self.client = client

    @classmethod
    def from_creds(cls, api_key: str, api_token: str) -> TrelloAdapter:
        """Initialize with API Key and API Token."""
        return cls(TrelloClient(api_key=api_key, api_secret=api_token))

    def get_member(self) -> Member:
        """Get member information."""
        return self.client.get_member("me")

    def get_boards(self) -> dict[str, dict[str, str]]:
        """Get all user's boards."""
        return {
            board.id: {"id": board.id, "name": board.name}
            for board in self.client.list_boards(board_filter="open")
        }
