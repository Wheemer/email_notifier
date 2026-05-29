# ***********************************************************************************************************************************************
# Purpose:  Config flow for Email Client integration
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
"""Config flow for Email Client integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowContext
from homeassistant.const import CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_ENCRYPTION,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_RECIPIENTS,
    CONF_SENDER,
    CONF_SENDER_NAME,
    CONF_SERVER,
    CONF_TEST_CONNECTION,
    CONF_TIMEOUT,
    CONF_USERNAME,
    DEFAULT_ENCRYPTION,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DOMAIN,
    ENCRYPTION_OPTIONS,
    GLOBAL_API,
)
from .smtp_api import SmtpAPI


# ***********************************************************************************************************************************************
# Purpose:  Test connection
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
def _test_connection(hass: HomeAssistant, user_input) -> bool:
    """Test the connection with the provided user input."""
    if DOMAIN not in hass.data:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][GLOBAL_API] = SmtpAPI(hass)
    api = hass.data[DOMAIN][GLOBAL_API]
    return api.connection_is_valid(_clean_config_data(user_input), True)


def _entry_sources(flow) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return options and data sources for a config or options flow."""
    entry = getattr(flow, "_entry", None)
    if entry is None:
        return {}, {}
    return entry.options, entry.data


def _get_config_value(flow, user_input: dict[str, Any], key: str, default: Any = None) -> Any:
    """Return a config value from form input, options, data, or default."""
    options, data = _entry_sources(flow)
    return user_input.get(key, options.get(key, data.get(key, default)))


def _get_text_config_value(flow, user_input: dict[str, Any], key: str, default: str = "") -> str:
    """Return a string-safe config value for text form fields."""
    value = _get_config_value(flow, user_input, key, default)
    if value is None:
        return ""
    return str(value)


def _clean_config_data(config_data: dict[str, Any]) -> dict[str, Any]:
    """Remove optional SMTP credentials unless both are provided."""
    data = dict(config_data)

    username = data.get(CONF_USERNAME, "")
    password = data.get(CONF_PASSWORD, "")
    if isinstance(username, str):
        username = username.strip()
    if isinstance(password, str):
        password = password.strip()

    if username and password:
        data[CONF_USERNAME] = username
        data[CONF_PASSWORD] = password
    else:
        data.pop(CONF_USERNAME, None)
        data.pop(CONF_PASSWORD, None)

    return data


def _merge_config_data(current_data: dict[str, Any], user_input: dict[str, Any]) -> dict[str, Any]:
    """Merge submitted form data and discard incomplete optional credentials."""
    return _clean_config_data({**current_data, **user_input})


# ***********************************************************************************************************************************************
# Purpose:  Get config flow schema
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
def get_schema(self, user_input: dict[str, Any] | None) -> vol.Schema:
    """Return schema."""
    if user_input is None:
        user_input = {}

    return vol.Schema(
    {
        vol.Required(
            CONF_SERVER,
            default = _get_text_config_value(self, user_input, CONF_SERVER),
        ): str,
        vol.Required(
            CONF_PORT,
            default = _get_config_value(self, user_input, CONF_PORT, DEFAULT_PORT),
        ): int,
        vol.Optional(
            CONF_USERNAME,
            default = _get_text_config_value(self, user_input, CONF_USERNAME),
        ): str,
        vol.Optional(
            CONF_PASSWORD,
            default = _get_text_config_value(self, user_input, CONF_PASSWORD),
        ): str,
        vol.Required(
            CONF_SENDER,
            default = _get_text_config_value(self, user_input, CONF_SENDER),
        ): str,
        vol.Required(
            CONF_RECIPIENTS,
            default = _get_text_config_value(self, user_input, CONF_RECIPIENTS),
        ): str,
        vol.Optional(
            CONF_SENDER_NAME,
            default = _get_text_config_value(self, user_input, CONF_SENDER_NAME, "Home Assistant"),
        ): str,
        vol.Required(
                CONF_ENCRYPTION,
                default = _get_config_value(self, user_input, CONF_ENCRYPTION, DEFAULT_ENCRYPTION),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options =  ENCRYPTION_OPTIONS,
                    translation_key = CONF_ENCRYPTION,
            )),
        vol.Required(
            CONF_TIMEOUT,
            default = _get_config_value(self, user_input, CONF_TIMEOUT, DEFAULT_TIMEOUT),
        ): int,
        vol.Optional(
            CONF_VERIFY_SSL,
            default = _get_config_value(self, user_input, CONF_VERIFY_SSL, True),
        ): bool,
        vol.Optional(CONF_TEST_CONNECTION, default = False): bool,
    })


# ***********************************************************************************************************************************************
# Purpose:  Configuration form for the integration (runs when integration entry is added)
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
class EmailClientConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Email Client."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult[ConfigFlowContext, str]:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if user_input.get(CONF_TEST_CONNECTION):
                if not _test_connection(self.hass,user_input):
                    errors["base"] = "connection_failed"
                    return self.async_show_form(step_id="user", data_schema=get_schema(self, user_input), errors=errors)
            return self.async_create_entry(title=user_input[CONF_SENDER], data=_clean_config_data(user_input))

        return self.async_show_form(step_id="user", data_schema=get_schema(self, user_input), errors=errors)


    # ***********************************************************************************************************************************************
    # Purpose:  Callback from options flow (must be inside class, otherwise the 'Configuration' link will not be displayed)
    # History:  D.Geisenhoff    24-JAN-2025     Created
    # ***********************************************************************************************************************************************
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return EmailClientOptionsFlow(config_entry)

    @property
    def _title_placeholders(self) -> dict[str, str]:
        """Return title placeholders for the entry."""
        return {"email": "Email Notifier"}


# ***********************************************************************************************************************************************
# Purpose:  Configuration form for options (runs when configuration link is clicked)
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
class EmailClientOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    # ***********************************************************************************************************************************************
    # Purpose:  Initialize the class.
    # History:  D.Geisenhoff    07-MAY-2025     Created
    # ***********************************************************************************************************************************************
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._entry = config_entry

    # ***********************************************************************************************************************************************
    # Purpose:  Show first (and in this case only) step of config form
    # History:  D.Geisenhoff    07-MAY-2025     Created
    # ***********************************************************************************************************************************************
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult[ConfigFlowContext, str]:
        """Manage the options."""
        if user_input is not None:
            if user_input.get(CONF_TEST_CONNECTION):
                if not _test_connection(self.hass,user_input):
                    return self.async_show_form(
                        step_id="init",
                        data_schema=get_schema(self, user_input),
                        errors={"base": "connection_failed"},
                    )
            # Merge user_input and config_entry.data into new dictionary and save back to config_entry.data
            # config_entry.option is not needed, because the info for creating an entry (data) and for editing an entry (option) is the same.
            new_data = _merge_config_data(self._entry.data, user_input)
            # async_update_entry saves the new changes
            self.hass.config_entries.async_update_entry(self._entry, data=new_data, title = user_input[CONF_SENDER])
            # Save back an empty object to config_entry.options
            return self.async_create_entry(title="", data = {})
        return self.async_show_form(step_id="init", data_schema=get_schema(self, user_input))
