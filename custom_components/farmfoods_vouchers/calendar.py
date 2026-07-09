from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FarmfoodsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: FarmfoodsCoordinator = entry_data["coordinator"]

    async_add_entities([FarmfoodsCalendarEntity(coordinator, entry)])


class FarmfoodsCalendarEntity(
    CoordinatorEntity[FarmfoodsCoordinator], CalendarEntity
):
    _attr_icon = "mdi:ticket-percent-outline"

    def __init__(self, coordinator: FarmfoodsCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{DOMAIN}_calendar_{entry.unique_id}"
        self._attr_name = f"{entry.title} Vouchers"

    @property
    def event(self) -> CalendarEvent | None:
        events = self._get_events_list()
        if not events:
            return None
        events.sort(key=lambda x: x.start)
        return events[0]

    def _get_events_list(self) -> list[CalendarEvent]:
        events = []
        sensor = self.coordinator.hass.data[DOMAIN][self._entry_id].get("sensor")
        used_ids = sensor._used_voucher_ids if sensor else set()

        for voucher in self.coordinator.data or []:
            try:
                start_date = datetime.strptime(
                    voucher["valid_from"], "%d/%m/%Y"
                ).date()
                end_date = datetime.strptime(
                    voucher["expires"], "%d/%m/%Y"
                ).date() + timedelta(days=1)
            except ValueError:
                continue

            is_used = voucher["id"] in used_ids
            prefix = "[Used] " if is_used else ""
            summary = f"{prefix}Farmfoods: {voucher['discount']}"
            description = (
                f"Code: {voucher['code']}\n"
                f"Valid From: {voucher['valid_from']}\n"
                f"Expires: {voucher['expires']}\n"
                f"Used: {'Yes' if is_used else 'No'}"
            )

            events.append(
                CalendarEvent(
                    summary=summary,
                    start=start_date,
                    end=end_date,
                    description=description,
                )
            )
        return events

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        start_d = start_date.date()
        end_d = end_date.date()

        filtered_events = []
        for event in self._get_events_list():
            if event.start < end_d and event.end > start_d:
                filtered_events.append(event)
        return filtered_events
