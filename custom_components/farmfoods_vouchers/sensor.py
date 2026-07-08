from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
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
    known_sensors: dict[str, FarmfoodsVoucherSensor] = entry_data["sensors"]

    def _build_new_sensors() -> list[FarmfoodsVoucherSensor]:
        new_sensors = []
        for voucher in coordinator.data or []:
            if voucher["id"] not in known_sensors:
                sensor = FarmfoodsVoucherSensor(coordinator, voucher)
                known_sensors[voucher["id"]] = sensor
                new_sensors.append(sensor)
        return new_sensors

    @callback
    def _on_coordinator_update() -> None:
        current_ids = {v["id"] for v in (coordinator.data or [])}
        entity_reg = er.async_get(hass)

        for voucher_id in list(known_sensors):
            if voucher_id not in current_ids:
                sensor = known_sensors.pop(voucher_id)
                if sensor.entity_id:
                    entity_reg.async_remove(sensor.entity_id)

        new_sensors = _build_new_sensors()
        if new_sensors:
            async_add_entities(new_sensors)

    async_add_entities(_build_new_sensors())
    entry.async_on_unload(coordinator.async_add_listener(_on_coordinator_update))


class FarmfoodsVoucherSensor(CoordinatorEntity[FarmfoodsCoordinator], SensorEntity, RestoreEntity):
    _attr_icon = "mdi:ticket-percent-outline"

    def __init__(self, coordinator: FarmfoodsCoordinator, voucher: dict) -> None:
        super().__init__(coordinator)
        self._voucher_id = voucher["id"]
        self._voucher = voucher
        self._used = False
        self._attr_unique_id = f"{DOMAIN}_{voucher['id']}"
        self._attr_name = f"Farmfoods {voucher['discount']}"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.attributes.get("used"):
            self._used = True

    @callback
    def _handle_coordinator_update(self) -> None:
        for voucher in self.coordinator.data or []:
            if voucher["id"] == self._voucher_id:
                self._voucher = voucher
                self.async_write_ha_state()
                return

    @property
    def native_value(self) -> str:
        return self._voucher["code"]

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "discount": self._voucher["discount"],
            "valid_from": self._voucher["valid_from"],
            "expires": self._voucher["expires"],
            "used": self._used,
        }

    def mark_used(self) -> None:
        self._used = True
        self.async_write_ha_state()
