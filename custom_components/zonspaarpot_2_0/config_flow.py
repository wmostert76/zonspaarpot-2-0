"""Config flow for Zonspaarpot 2.0."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ZonspaarpotApiClient, ZonspaarpotApiConnectionError, ZonspaarpotApiError
from .const import CONF_HOST, CONF_SCAN_INTERVAL, DEFAULT_HOST, DEFAULT_SCAN_INTERVAL, DOMAIN, NAME


class ZonspaarpotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zonspaarpot 2.0."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            scan_interval = int(user_input[CONF_SCAN_INTERVAL])

            session = async_get_clientsession(self.hass)
            api = ZonspaarpotApiClient(session, host)
            try:
                info = await api.async_get_info()
            except ZonspaarpotApiConnectionError:
                errors["base"] = "cannot_connect"
            except ZonspaarpotApiError:
                errors["base"] = "invalid_api"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                title = info.get("product_name") or NAME
                unique_id = f"{DOMAIN}_{host}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_HOST: host,
                        CONF_SCAN_INTERVAL: scan_interval,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=2, max=300)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return ZonspaarpotOptionsFlow(config_entry)


class ZonspaarpotOptionsFlow(config_entries.OptionsFlow):
    """Handle Zonspaarpot options."""

    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = int(
            self._config_entry.options.get(
                CONF_SCAN_INTERVAL,
                self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=2, max=300)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
