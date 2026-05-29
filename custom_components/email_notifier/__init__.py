# ***********************************************************************************************************************************************
# Purpose:  An email notification service integration
# History:  D.Geisenhoff    06-JUN-2025 Created
#           D.Geisenhoff    26-DEC-2025 Merged pull request from onoffautomations:
#                                       - Updated service schema to include new fields
#                                       - Changed images and attachments to accept string input (multiline)
#                                       - Added parsing logic to convert multiline string input to lists
#                                       - Updated async_send_email() to pass new parameters
# ***********************************************************************************************************************************************
"""Email Notification Service integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_registry as er

from .const import (
    ATTR_ATTACHMENTS,
    ATTR_FROM_ADDRESS,
    ATTR_HTML,
    ATTR_IMAGES,
    ATTR_REPLY_TO,
    ATTR_SENDER_NAME,
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
    DOMAIN,
    ENCRYPTION_OPTIONS,
    GLOBAL_API,
    GLOBAL_COUNTER,
    PLATFORM,
)
from .smtp_api import SmtpAPI

_LOGGER = logging.getLogger(__name__)
SERVICE_SEND = "send"
ATTR_ACCOUNT = "account"
ATTR_TITLE = "title"
ATTR_MESSAGE = "message"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_SERVER): cv.string,
                vol.Required(CONF_PORT): cv.port,
                vol.Optional(CONF_USERNAME): cv.string,
                vol.Optional(CONF_PASSWORD): cv.string,
                vol.Required(CONF_SENDER): cv.string,
                vol.Required(CONF_RECIPIENTS): cv.string,
                vol.Optional(CONF_SENDER_NAME): cv.string,
                vol.Required(CONF_ENCRYPTION): vol.In(ENCRYPTION_OPTIONS),
                vol.Required(CONF_TIMEOUT): cv.positive_int,
                vol.Optional(CONF_VERIFY_SSL, default=True): cv.boolean,
                vol.Optional(CONF_TEST_CONNECTION): cv.boolean
            }
        )
    },
    extra=vol.ALLOW_EXTRA,  # Allow additional keys in YAML
)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ACCOUNT): cv.string,
        vol.Optional(CONF_RECIPIENTS): cv.string,
        vol.Optional(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_HTML): cv.string,
        vol.Optional(ATTR_IMAGES): cv.string,
        vol.Optional(ATTR_ATTACHMENTS): cv.string,
        vol.Optional(ATTR_FROM_ADDRESS): cv.string,
        vol.Optional(ATTR_SENDER_NAME): cv.string,
        vol.Optional(ATTR_REPLY_TO): cv.string,
    }
)


# ***********************************************************************************************************************************************
# Purpose:  Initialize global variables
# History:  D.Geisenhoff    29-MAY-2025     Created
# ***********************************************************************************************************************************************
def init_vars(hass: HomeAssistant):
    """Initialize global variables for the Whatsigram Messenger component."""
    # Set a global counter for the entity id (entity id should not change after entity has been created, so the name of the sender cannot be taken)
    # The entity id will be notify_whatsigram_recipient_1, ...recipient_2, ...
    if GLOBAL_COUNTER not in hass.data[DOMAIN]:
        hass.data[DOMAIN][GLOBAL_COUNTER] = 1
    else:
        hass.data[DOMAIN][GLOBAL_COUNTER] += 1


def _split_multiline(value):
    """Return non-empty lines from a multiline service field."""
    if isinstance(value, str):
        return [line.strip() for line in value.split("\n") if line.strip()]
    return value


# ***********************************************************************************************************************************************
# Purpose:  Send message callback function of service
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
async def async_send_email(call):
    """Send an email."""
    data = {}
    if call.data.get(ATTR_HTML):
        data[ATTR_HTML] = call.data.get(ATTR_HTML)
    if call.data.get(ATTR_IMAGES):
        data[ATTR_IMAGES] = _split_multiline(call.data.get(ATTR_IMAGES))
    if call.data.get(ATTR_ATTACHMENTS):
        data[ATTR_ATTACHMENTS] = _split_multiline(call.data.get(ATTR_ATTACHMENTS))
    if call.data.get(ATTR_ACCOUNT):
        data[ATTR_ACCOUNT] = call.data.get(ATTR_ACCOUNT)
    if call.data.get(CONF_RECIPIENTS):
        data[CONF_RECIPIENTS] = call.data.get(CONF_RECIPIENTS)
    if call.data.get(ATTR_FROM_ADDRESS):
        data[ATTR_FROM_ADDRESS] = call.data.get(ATTR_FROM_ADDRESS)
    if call.data.get(ATTR_SENDER_NAME):
        data[ATTR_SENDER_NAME] = call.data.get(ATTR_SENDER_NAME)
    if call.data.get(ATTR_REPLY_TO):
        data[ATTR_REPLY_TO] = call.data.get(ATTR_REPLY_TO)
    # Get sender entity
    entity_reg = er.async_get(call.hass)
    entity = entity_reg.async_get(data[ATTR_ACCOUNT])
    if entity is None:
        _LOGGER.error("No entity found for account %s", data[ATTR_ACCOUNT])
        return
    # Run send_message function of entity
    await call.hass.data[DOMAIN][entity.config_entry_id].send_message(call.data.get(ATTR_MESSAGE, ""), call.data.get(ATTR_TITLE, "Home Assistant"), data)



# ***********************************************************************************************************************************************
# Purpose:  Setup when Home Assistant starts, can run after or before setup_entry
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
async def async_setup(hass, config):
    """Set up the component."""
    # Register the service
    if DOMAIN not in hass.data:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][GLOBAL_API] = SmtpAPI(hass)
    if SERVICE_SEND in hass.services.async_services().get(DOMAIN, {}):
        _LOGGER.info("Service %s.%s is already registered.", DOMAIN, SERVICE_SEND)
    else:
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND,
            async_send_email,
            schema=SERVICE_SCHEMA,
        )
    return True


# ***********************************************************************************************************************************************
# Purpose:  Setup entities. Run when Home Assist is started, or entry is added. Can run after or before setup
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Email Client from a config entry."""
    if DOMAIN not in hass.data:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][GLOBAL_API] = SmtpAPI(hass)
    init_vars(hass)
    hass.data[DOMAIN][entry.entry_id] = {}
    # Set up notify platform
    await hass.config_entries.async_forward_entry_setups(entry, [PLATFORM])
    # Add a listener for config changes and remove when entity is unloaded
    #entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


# ***********************************************************************************************************************************************
# Purpose:  Update entity name, when configuration changes
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
# async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
#     """Update entry title and entity name."""
#     hass.config_entries.async_update_entry(entry,title=entry.options.get("sender", entry.data.get("sender")))
#     entity_reg = er.async_get(hass)
#     entities = er.async_entries_for_config_entry(entity_reg, entry.entry_id)
#     entity_reg.async_update_entity(entities[0].entity_id, _attr_translation_placeholders = {"sender": entry.options.get("sender", entry.data.get("sender"))})


# ***********************************************************************************************************************************************
# Purpose:  Called when entry is unloaded
# History:  D.Geisenhoff    07-MAY-2025     Created
# ***********************************************************************************************************************************************
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_forward_entry_unload(entry, PLATFORM):
        hass.data[DOMAIN].pop(entry.entry_id)
        config_entries = hass.config_entries.async_entries(DOMAIN)
        num_entries = len(config_entries)
        if num_entries == 1:
            # Unregister the service, when last entry is removed
            hass.services.async_remove(DOMAIN, SERVICE_SEND)
            # Remove all domain data
            hass.data.pop(DOMAIN)
    return unload_ok
