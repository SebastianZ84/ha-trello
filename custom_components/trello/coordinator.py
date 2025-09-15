"""Data update coordinator for the Trello integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from trello import TrelloClient

from .const import LOGGER, Board, List, Card, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL


class TrelloDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Board]]):
    """Data update coordinator for the Trello integration."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, trello_client: TrelloClient, board_ids: list[str], config_entry: ConfigEntry = None
    ) -> None:
        """Initialize the coordinator."""
        # Get update interval from config, default to 20 seconds
        update_interval = DEFAULT_UPDATE_INTERVAL
        if config_entry and config_entry.options.get(CONF_UPDATE_INTERVAL):
            update_interval = config_entry.options[CONF_UPDATE_INTERVAL]
        
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name="trello",
            update_interval=timedelta(seconds=update_interval),
        )
        self.client = trello_client
        self.board_ids = board_ids

    def _update(self) -> dict[str, Board]:
        """Fetch data for all boards."""
        board_id_boards: dict[str, Board] = {}
        
        for board_id in self.board_ids:
            try:
                LOGGER.debug("Fetching board %s", board_id)
                board = self.client.get_board(board_id)
                lists = board.list_lists(list_filter='open')
                
                # Get cards for each list
                board_lists = {}
                for trello_list in lists:
                    cards = trello_list.list_cards()
                    card_objects = [
                        Card(
                            id=card.id,
                            name=card.name,
                            desc=getattr(card, 'desc', ''),
                            due=getattr(card, 'due', None),
                            list_id=trello_list.id
                        )
                        for card in cards
                    ]
                    
                    board_lists[trello_list.id] = List(
                        trello_list.id,
                        trello_list.name,
                        len(card_objects),
                        card_objects
                    )
                
                board_id_boards[board_id] = Board(board_id, board.name, board_lists)
                
            except Exception as e:
                LOGGER.error("Unable to fetch board %s: %s", board_id, e)
                board_id_boards[board_id] = Board(board_id, "", {})
        
        return board_id_boards

    async def _async_update_data(self) -> dict[str, Board]:
        """Send request to the executor."""
        return await self.hass.async_add_executor_job(self._update)


