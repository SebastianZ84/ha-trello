"""Data update coordinator for the Trello integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from trello import Board as TrelloBoard
from trello import List as TrelloList
from trello import TrelloClient
from trello.batch.board import Board as BatchBoard

from .const import LOGGER, Board, List, Card


class TrelloDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Board]]):
    """Data update coordinator for the Trello integration."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, trello_client: TrelloClient, board_ids: list[str]
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name="trello",
            update_interval=timedelta(seconds=60),
        )
        self.client = trello_client
        self.board_ids = board_ids

    def _update(self) -> dict[str, Board]:
        """Fetch data for all sensors as a batch."""
        batch_requests = []
        for board_id in self.board_ids:
            batch_requests.append(BatchBoard.GetBoard(board_id, ['name']))
            batch_requests.append(BatchBoard.GetLists(board_id, ['name'], 'open', ['cards']))
            batch_requests.append(BatchBoard.GetCards(board_id, ['name', 'desc', 'due', 'idList']))
        LOGGER.debug("Fetching boards lists")
        batch_responses = self.client.fetch_batch(batch_requests)

        return _get_boards(batch_responses, self.board_ids)

    async def _async_update_data(self) -> dict[str, Board]:
        """Send request to the executor."""
        return await self.hass.async_add_executor_job(self._update)


def _get_boards(batch_response: list[dict], board_ids: list[str]) -> dict[str, Board]:
    board_id_boards: dict[str, Board] = {}
    for i, batch_response_triple in enumerate(
        zip(batch_response[::3], batch_response[1::3], batch_response[2::3])
    ):
        board_response = batch_response_triple[0]
        list_response = batch_response_triple[1] 
        card_response = batch_response_triple[2]
        if board_response.success and list_response.success and card_response.success:
            board = board_response.payload
            lists = list_response.payload
            cards = card_response.payload
            board_id_boards[board.id] = _get_board(board, lists, cards)
        else:
            LOGGER.error(
                "Unable to fetch data for board with ID '%s'. Board: %s, Lists: %s, Cards: %s",
                board_ids[i],
                board_response.success,
                list_response.success, 
                card_response.success,
            )
            board_id_boards[board_ids[i]] = Board(board_ids[i], "", {})
            continue

    return board_id_boards


def _get_board(board: TrelloBoard, lists: list[TrelloList], cards: list) -> Board:
    # Group cards by list ID
    cards_by_list = {}
    for card in cards:
        list_id = card.idList
        if list_id not in cards_by_list:
            cards_by_list[list_id] = []
        cards_by_list[list_id].append(
            Card(
                id=card.id,
                name=card.name,
                desc=card.desc,
                due=getattr(card, 'due', None),
                list_id=list_id
            )
        )
    
    return Board(
        board.id,
        board.name,
        {
            list_.id: List(
                list_.id, 
                list_.name, 
                len(cards_by_list.get(list_.id, [])),
                cards_by_list.get(list_.id, [])
            )
            for list_ in lists
        },
    )
