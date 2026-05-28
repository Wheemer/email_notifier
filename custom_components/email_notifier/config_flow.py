# ***********************************************************************************************************************************************
# Purpose:  Config flow for Email Client integration
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
"""Config flow for Email Client integration."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowContext
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
    CONF_SMTP_AUTH,
    CONF_TEST_CONNECTION,
    CONF_TIMEOUT,
    CONF_USERNAME,
    DEFAULT_ENCRYPTION,
    DEFAULT_PORT,
    DEFAULT_SMTP_AUTH,
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
    return api.connection_is_valid(user_input, True)



def _get_config_value(config_entry, user_input: dict[str, Any], key: str, default: Any = None) -> Any:
    """Return a config value from form input, options, data, or default."""
    return user_input.get(key, config_entry.options.get(key, config_entry.data.get(key, default)))



def _auth_fields_present(user_input: dict[str, Any]) -> bool:
    """Return true if auth fields were submitted from an auth-enabled form."""
    return CONF_USERNAME in user_input or CONF_PASSWORD in user_input



def _strip_auth_fields(user_input: dict[str, Any]) -> dict[str, Any]:
    """Remove auth-only fields when SMTP authentication is disabled."""
    return {
        key: value
        for key, value in user_input.items()
        if key not in (CONF_USERNAME, CONF_PASSWORD)
    }



# ***********************************************************************************************************************************************
# Purpose:  Get config flow schema
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
def get_schema(self, user_input: dict[str, Any] | None) -> vol.Schema:
    """Return schema."""
    if user_input is None:
        user_input = {}
    if hasattr(self, "_entry"):
        config_entry = self._entry
    else:
        config_entry =  SimpleNamespace()
        config_entry.options = {}
        config_entry.data = {}

    smtp_auth = _get_config_value(config_entry, user_input, CONF_SMTP_AUTH, DEFAULT_SMTP_AUTH)
    schema = {
        vol.Required(
            CONF_SERVER,
            default = _get_config_value(config_entry, user_input, CONF_SERVER),
        ): str,
        vol.Required(
            CONF_PORT,
            default = _get_config_value(config_entry, user_input, CONF_PORT, DEFAULT_PORT),
        ): int,
        vol.Optional(
            CONF_SMTP_AUTH,
            default = smtp_auth,
        ): bool,
        vol.Required(
            CONF_SENDER,
            default = _get_config_value(config_entry, user_input, CONF_SENDER),
        ): str,
        vol.Required(
            CONF_RECIPIENTS,
            default = _get_config_value(config_entry, user_input, CONF_RECIPIENTS),
        ): str,
        vol.Optional(
            CONF_SENDER_NAME,
            default = _get_config_value(config_entry, user_input, CONF_SENDER_NAME, "Home Assistant"),
        ): str,
        vol.Required(
                CONF_ENCRYPTION,
                default = _get_config_value(config_entry, user_input, CONF_ENCRYPTION, DEFAULT_ENCRYPTION),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options =  ENCRYPTION_OPTIONS,
                    translation_key = CONF_ENCRYPTION,
            )),
        vol.Required(
            CONF_TIMEOUT,
            default = _get_config_value(config_entry, user_input, CONF_TIMEOUT, DEFAULT_TIMEOUT),
        ): int,
        vol.Optional(CONF_TEST_CONNECTION, default = False): bool,
    }
    if smtp_auth:
        schema.update(
            {
                vol.Required(
                    CONF_USERNAME,
                    default = _get_config_value(config_entry, user_input, CONF_USERNAME),
                ): str,
                vol.Required(
                    CONF_PASSWORD,
                    default = _get_config_value(config_entry, user_input, CONF_PASSWORD),
                ): str,
            }
        )
    return vol.Schema(schema)



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
            if not user_input.get(CONF_SMTP_AUTH, DEFAULT_SMTP_AUTH) and _auth_fields_present(user_input):
                user_input = _strip_auth_fields(user_input)
                return self.async_show_form(step_id="user", data_schema=get_schema(self, user_input), errors=errors)
            if user_input.get(CONF_TEST_CONNECTION):
                if not _test_connection(self.hass,user_input):
                    errors["base"] = "connection_failed"
                    return self.async_show_form(step_id="user", data_schema=get_schema(self, user_input), errors=errors)
            return self.async_create_entry(title=user_input[CONF_SENDER], data=user_input)

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
        """Return title placeholders fuer die Entry."""
        return {"email": "test@microteq.ch"}


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
            if not user_input.get(CONF_SMTP_AUTH, DEFAULT_SMTP_AUTH) and _auth_fields_present(user_input):
                user_input = _strip_auth_fields(user_input)
                return self.async_show_form(step_id="init", data_schema=get_schema(self, user_input))
            if user_input.get(CONF_TEST_CONNECTION):
                if not _test_connection(self.hass,user_input):
                    return self.async_show_form(
                        step_id="init",
                        data_schema=get_schema(self, user_input),
                        errors={"base": "connection_failed"},
                    )
            # Merge user_input and config_entry.data into new dictionary and save back to config_entry.data
            # config_entry.option is not needed, because the info for creating an entry (data) and for editing an entry (option) is the same.
            new_data = {**self._entry.data, **user_input}
            # async_update_entry saves the new changes
            self.hass.config_entries.async_update_entry(self._entry, data=new_data, title = user_input[CONF_SENDER])
            # Save back an empty object to config_entry.options
            return self.async_create_entry(title="", data = {})
        return self.async_show_form(step_id="init", data_schema=get_schema(self, user_input))
