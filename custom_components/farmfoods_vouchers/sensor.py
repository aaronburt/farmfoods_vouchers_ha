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

    sensor = FarmfoodsVouchersSensor(coordinator, entry)
    entry_data["sensor"] = sensor

    async_add_entities([sensor])


class FarmfoodsVouchersSensor(
    CoordinatorEntity[FarmfoodsCoordinator], SensorEntity, RestoreEntity
):
    _attr_icon = "mdi:ticket-percent-outline"

    def __init__(self, coordinator: FarmfoodsCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{DOMAIN}_vouchers_{entry.unique_id}"
        self._attr_name = f"{entry.title} Vouchers"
        self._used_voucher_ids: set[str] = set()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            restored_vouchers = last_state.attributes.get("vouchers") or []
            for voucher in restored_vouchers:
                if voucher.get("used"):
                    self._used_voucher_ids.add(voucher["id"])

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data:
            current_ids = {v["id"] for v in self.coordinator.data}
            self._used_voucher_ids &= current_ids
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return sum(
            1 for v in self.coordinator.data if v["id"] not in self._used_voucher_ids
        )

    @property
    def extra_state_attributes(self) -> dict:
        vouchers = []
        for voucher in self.coordinator.data or []:
            vouchers.append(
                {
                    "id": voucher["id"],
                    "code": voucher["code"],
                    "discount": voucher["discount"],
                    "valid_from": voucher["valid_from"],
                    "expires": voucher["expires"],
                    "used": voucher["id"] in self._used_voucher_ids,
                }
            )
        return {
            "vouchers": vouchers,
            "total_vouchers": len(self.coordinator.data or []),
            "unused_vouchers": self.native_value,
        }

    def mark_used(self, voucher_id: str | None = None, code: str | None = None) -> bool:
        target_id = None
        if voucher_id:
            target_id = voucher_id
        elif code:
            for voucher in self.coordinator.data or []:
                if voucher["code"] == code:
                    target_id = voucher["id"]
                    break

        if target_id and target_id not in self._used_voucher_ids:
            self._used_voucher_ids.add(target_id)
            self.async_write_ha_state()
            return True
        return False

    def mark_unused(
        self, voucher_id: str | None = None, code: str | None = None
    ) -> bool:
        target_id = None
        if voucher_id:
            target_id = voucher_id
        elif code:
            for voucher in self.coordinator.data or []:
                if voucher["code"] == code:
                    target_id = voucher["id"]
                    break

        if target_id and target_id in self._used_voucher_ids:
            self._used_voucher_ids.remove(target_id)
            self.async_write_ha_state()
            return True
        return False
