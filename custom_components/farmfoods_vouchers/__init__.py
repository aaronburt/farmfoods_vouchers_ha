import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import FarmfoodsCoordinator

PLATFORMS = [Platform.SENSOR]

SERVICE_MARK_USED_SCHEMA = vol.Schema(
    vol.All(
        {
            vol.Optional("code"): cv.string,
            vol.Optional("id"): cv.string,
        },
        cv.has_at_least_one_key("code", "id"),
    )
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = FarmfoodsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "sensor": None,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def async_handle_mark_used(call: ServiceCall) -> None:
        code = call.data.get("code")
        voucher_id = call.data.get("id")
        for entry_data in hass.data[DOMAIN].values():
            sensor = entry_data.get("sensor")
            if sensor:
                sensor.mark_used(voucher_id=voucher_id, code=code)

    async def async_handle_mark_unused(call: ServiceCall) -> None:
        code = call.data.get("code")
        voucher_id = call.data.get("id")
        for entry_data in hass.data[DOMAIN].values():
            sensor = entry_data.get("sensor")
            if sensor:
                sensor.mark_unused(voucher_id=voucher_id, code=code)

    if not hass.services.has_service(DOMAIN, "mark_used"):
        hass.services.async_register(
            DOMAIN,
            "mark_used",
            async_handle_mark_used,
            schema=SERVICE_MARK_USED_SCHEMA,
        )
    if not hass.services.has_service(DOMAIN, "mark_unused"):
        hass.services.async_register(
            DOMAIN,
            "mark_unused",
            async_handle_mark_unused,
            schema=SERVICE_MARK_USED_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    if not hass.data[DOMAIN]:
        if hass.services.has_service(DOMAIN, "mark_used"):
            hass.services.async_remove(DOMAIN, "mark_used")
        if hass.services.has_service(DOMAIN, "mark_unused"):
            hass.services.async_remove(DOMAIN, "mark_unused")

    return unload_ok
