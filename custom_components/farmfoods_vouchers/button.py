from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import FarmfoodsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: FarmfoodsCoordinator = entry_data["coordinator"]
    known_buttons: dict[str, FarmfoodsMarkUsedButton] = entry_data["buttons"]

    def _build_new_buttons() -> list[FarmfoodsMarkUsedButton]:
        new_buttons = []
        for voucher in coordinator.data or []:
            if voucher["id"] not in known_buttons:
                button = FarmfoodsMarkUsedButton(hass, entry, voucher)
                known_buttons[voucher["id"]] = button
                new_buttons.append(button)
        return new_buttons

    @callback
    def _on_coordinator_update() -> None:
        current_ids = {v["id"] for v in (coordinator.data or [])}
        entity_reg = er.async_get(hass)

        for voucher_id in list(known_buttons):
            if voucher_id not in current_ids:
                button = known_buttons.pop(voucher_id)
                if button.entity_id:
                    entity_reg.async_remove(button.entity_id)

        new_buttons = _build_new_buttons()
        if new_buttons:
            async_add_entities(new_buttons)

    async_add_entities(_build_new_buttons())
    entry.async_on_unload(coordinator.async_add_listener(_on_coordinator_update))


class FarmfoodsMarkUsedButton(ButtonEntity):
    _attr_icon = "mdi:check-circle-outline"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        voucher: dict,
    ) -> None:
        self._hass = hass
        self._entry_id = entry.entry_id
        self._voucher_id = voucher["id"]
        self._attr_unique_id = f"{DOMAIN}_{voucher['id']}_mark_used"
        self._attr_name = f"Mark as Used: {voucher['discount']}"

    async def async_press(self) -> None:
        sensors = self._hass.data[DOMAIN][self._entry_id]["sensors"]
        sensor = sensors.get(self._voucher_id)
        if sensor:
            sensor.mark_used()
