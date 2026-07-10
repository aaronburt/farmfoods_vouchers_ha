import asyncio
from datetime import timedelta
import logging
import random
from urllib.parse import urlparse

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_VOUCHER_URL, DOMAIN
from .parser import parse_vouchers

_LOGGER = logging.getLogger(__name__)


class FarmfoodsCoordinator(DataUpdateCoordinator[list[dict]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=random.randint(12 * 3600, 16 * 3600)
            ),
        )
        self._voucher_url: str = entry.data[CONF_VOUCHER_URL]
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> list[dict]:
        self.update_interval = timedelta(
            seconds=random.randint(12 * 3600, 16 * 3600)
        )
        parsed_url = urlparse(self._voucher_url)
        if parsed_url.netloc.lower() not in ("farmfoods.co.uk", "www.farmfoods.co.uk"):
            raise UpdateFailed("Invalid voucher URL domain")

        try:
            async with asyncio.timeout(15):
                async with self._session.get(self._voucher_url) as response:
                    response.raise_for_status()
                    html = await response.text()
            return parse_vouchers(html)
        except Exception as err:
            raise UpdateFailed(f"Error fetching Farmfoods vouchers: {err}") from err
