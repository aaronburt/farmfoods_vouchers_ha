import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import FarmfoodsCoordinator

PLATFORMS = [Platform.SENSOR]

SERVICE_SCHEMA = vol.Schema(
    vol.All(
        {
            vol.Optional("code"): cv.string,
            vol.Optional("id"): cv.string,
        },
        cv.has_at_least_one_key("code", "id"),
    )
)

SERVICES = ("mark_used", "mark_unused")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = FarmfoodsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "sensor": None,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    def _apply_to_sensors(method_name: str, call: ServiceCall) -> None:
        code = call.data.get("code")
        voucher_id = call.data.get("id")
        for entry_data in hass.data[DOMAIN].values():
            sensor = entry_data.get("sensor")
            if sensor:
                getattr(sensor, method_name)(voucher_id=voucher_id, code=code)

    for service_name in SERVICES:
        if not hass.services.has_service(DOMAIN, service_name):
            hass.services.async_register(
                DOMAIN,
                service_name,
                lambda call, m=service_name: _apply_to_sensors(m, call),
                schema=SERVICE_SCHEMA,
            )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    if not hass.data[DOMAIN]:
        for service_name in SERVICES:
            if hass.services.has_service(DOMAIN, service_name):
                hass.services.async_remove(DOMAIN, service_name)

    return unload_ok
