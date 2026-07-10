import asyncio
from urllib.parse import parse_qs, urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_VOUCHER_URL, DOMAIN, REQUIRED_URL_PARAMS
from .parser import active_vouchers_section_exists

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_VOUCHER_URL): str,
})


class FarmfoodsVouchersConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_VOUCHER_URL].strip()
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)

            if (
                parsed_url.netloc.lower() not in ("farmfoods.co.uk", "www.farmfoods.co.uk")
                or not REQUIRED_URL_PARAMS.issubset(params.keys())
            ):
                errors[CONF_VOUCHER_URL] = "invalid_url"
            else:
                try:
                    session = async_get_clientsession(self.hass)
                    async with asyncio.timeout(15):
                        async with session.get(url) as response:
                            response.raise_for_status()
                            html = await response.text()

                    if not active_vouchers_section_exists(html):
                        errors[CONF_VOUCHER_URL] = "invalid_url"
                    else:
                        email = params["email_address"][0]
                        await self.async_set_unique_id(email)
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title=f"Farmfoods ({email})",
                            data={CONF_VOUCHER_URL: url},
                        )
                except config_entries.AbortFlow:
                    raise
                except Exception:
                    errors[CONF_VOUCHER_URL] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
