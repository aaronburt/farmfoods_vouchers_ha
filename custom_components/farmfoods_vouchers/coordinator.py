import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_VOUCHER_URL, DEFAULT_SCAN_INTERVAL_HOURS, DOMAIN
from .parser import parse_vouchers

_LOGGER = logging.getLogger(__name__)


class FarmfoodsCoordinator(DataUpdateCoordinator[list[dict]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=DEFAULT_SCAN_INTERVAL_HOURS),
        )
        self._voucher_url: str = entry.data[CONF_VOUCHER_URL]
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> list[dict]:
        try:
            async with asyncio.timeout(15):
                async with self._session.get(self._voucher_url) as response:
                    response.raise_for_status()
                    html = await response.text()
            return parse_vouchers(html)
        except Exception as err:
            raise UpdateFailed(f"Error fetching Farmfoods vouchers: {err}") from err
