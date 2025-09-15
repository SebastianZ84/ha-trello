"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, Board, List
from .coordinator import TrelloDataUpdateCoordinator


class TrelloSensor(CoordinatorEntity[TrelloDataUpdateCoordinator], SensorEntity):
    """Representation of a TrelloSensor."""

    _attr_native_unit_of_measurement = "Cards"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_icon = "mdi:format-list-bulleted"

    def __init__(
        self,
        board: Board,
        list_: List,
        coordinator: TrelloDataUpdateCoordinator,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.board = board
        self.list_id = list_.id
        self._attr_unique_id = f"trello_list_{list_.id}".lower()
        self._attr_name = list_.name

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, board.id)},
            name=board.name,
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Trello",
            model="Board",
        )

    @property
    def available(self) -> bool:
        """Determine if sensor is available."""
        board = self.coordinator.data[self.board.id]
        list_id = board.lists.get(self.list_id)
        return bool(board.lists and list_id)

    @property
    def native_value(self) -> int | None:
        """Return the card count of the sensor's list."""
        return self.coordinator.data[self.board.id].lists[self.list_id].card_count

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes - lightweight reference to board sensor."""
        board_data = self.coordinator.data[self.board.id]
        list_data = board_data.lists[self.list_id]
        return {
            "board_id": self.board.id,
            "board_name": board_data.name,
            "list_id": self.list_id,
            "list_name": list_data.name,
            "board_entity": f"sensor.{board_data.name.lower().replace(' ', '_').replace('-', '_')}_board",
            # Card data removed - reference board sensor instead
            "card_count": list_data.card_count
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.available:
            board = self.coordinator.data[self.board.id]
            self._attr_name = board.lists[self.list_id].name
            self.async_write_ha_state()
        super()._handle_coordinator_update()


class TrelloBoardSensor(CoordinatorEntity[TrelloDataUpdateCoordinator], SensorEntity):
    """Representation of a Trello Board sensor."""

    _attr_native_unit_of_measurement = "Lists"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_icon = "mdi:view-dashboard"

    def __init__(
        self,
        board: Board,
        coordinator: TrelloDataUpdateCoordinator,
    ) -> None:
        """Initialize board sensor."""
        super().__init__(coordinator)
        self.board = board
        self._attr_unique_id = f"trello_board_{board.id}".lower()
        self._attr_name = board.name

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, board.id)},
            name=board.name,
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Trello",
            model="Board",
        )

    @property
    def available(self) -> bool:
        """Determine if sensor is available."""
        return self.board.id in self.coordinator.data

    @property
    def native_value(self) -> int | None:
        """Return the number of lists in the board."""
        if self.board.id in self.coordinator.data:
            return len(self.coordinator.data[self.board.id].lists)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes with complete board data."""
        if self.board.id not in self.coordinator.data:
            return {}
            
        board_data = self.coordinator.data[self.board.id]
        return {
            "board_id": self.board.id,
            "board_name": board_data.name,
            "board_data": {
                "id": board_data.id,
                "name": board_data.name,
                "lists": {
                    list_id: {
                        "id": list_data.id,
                        "name": list_data.name,
                        "card_count": list_data.card_count,
                        "cards": [
                            {
                                "id": card.id,
                                "name": card.name,
                                "desc": card.desc,
                                "due": card.due,
                                "list_id": card.list_id
                            }
                            for card in list_data.cards
                        ]
                    }
                    for list_id, list_data in board_data.lists.items()
                }
            }
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.available:
            board_data = self.coordinator.data[self.board.id]
            self._attr_name = board_data.name
            self.async_write_ha_state()
        super()._handle_coordinator_update()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up trello sensors for config entries."""
    trello_coordinator: TrelloDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    boards = trello_coordinator.data.values()

    entities = []
    
    # Add board sensors (one per board)
    for board in boards:
        entities.append(TrelloBoardSensor(board, trello_coordinator))
    
    # Add list sensors (one per list)  
    for board in boards:
        for list_ in board.lists.values():
            entities.append(TrelloSensor(board, list_, trello_coordinator))

    async_add_entities(entities, True)
