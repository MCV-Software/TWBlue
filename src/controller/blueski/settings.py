from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

fromapprove.forms import Form, SubmitField, TextAreaField, TextField
fromapprove.translation import translate as _

if TYPE_CHECKING:
    fromapprove.config import ConfigSectionProxy
    fromapprove.sessions.blueski.session import Session as BlueskiSession # Adjusted

logger = logging.getLogger(__name__)

# This file is for defining forms and handling for Blueski-specific settings
# that might be more complex than simple key-value pairs handled by Session.get_settings_inputs.
# For Blueski, initial settings might be simple (handle, app password),
# but this structure allows for expansion.


class BlueskiSettingsForm(Form):
    """
    A settings form for Blueski sessions.
    This would mirror the kind of settings found in Session.get_settings_inputs
    but using the WTForms-like Form structure for more complex validation or layout.
    """
    # Example fields - these should align with what BlueskiSession.get_settings_inputs defines
    # and what BlueskiSession.get_configurable_values expects for its config.

    # instance_url = TextField(
    #     _("Instance URL"),
    #     default="https://bsky.social", # Default PDS for Bluesky
    #     description=_("The base URL of your Blueski PDS instance (e.g., https://bsky.social)."),
    #     validators=[], # Add validators if needed, e.g., URL validator
    # )
    handle = TextField(
        _("Bluesky Handle"),
        description=_("Your Bluesky user handle (e.g., @username.bsky.social or username.bsky.social)."),
        validators=[], # e.g., DataRequired()
    )
    app_password = TextField( # Consider PasswordField if sensitive and your Form class supports it
        _("App Password"),
        description=_("Your Bluesky App Password. Generate this in your Bluesky account settings."),
        validators=[], # e.g., DataRequired()
    )
    # Add more fields as needed for Blueski configuration.
    # For example, if there were specific notification settings, content filters, etc.

    submit = SubmitField(_("Save Blueski Settings"))


async def get_settings_form(
    user_id: str,
    session: BlueskiSession | None = None,
    config: ConfigSectionProxy | None = None, # User-specific config for Blueski
) -> BlueskiSettingsForm:
    """
    Creates and pre-populates the Blueski settings form.
    """
    form_data = {}
    if session: # If a session exists, use its current config
        # form_data["instance_url"] = session.config_get("api_base_url", "https://bsky.social")
        form_data["handle"] = session.config_get("handle", "")
        # App password should not be pre-filled for security.
        form_data["app_password"] = ""
    elif config: # Fallback to persisted config if no active session
        # form_data["instance_url"] = config.api_base_url.get("https://bsky.social")
        form_data["handle"] = config.handle.get("")
        form_data["app_password"] = ""

    form = BlueskiSettingsForm(formdata=None, **form_data) # formdata=None for initial display
    return form


async def process_settings_form(
    form: BlueskiSettingsForm,
    user_id: str,
    session: BlueskiSession | None = None, # Pass if update should affect live session
    config: ConfigSectionProxy | None = None, # User-specific config for Blueski
) -> bool:
    """
    Processes the submitted Blueski settings form and updates configuration.
    Returns True if successful, False otherwise.
    """
    if not form.validate(): # Assuming form has a validate method
        logger.warning(f"Blueski settings form validation failed for user {user_id}: {form.errors}")
        return False

    if not config and session: # Try to get config via session if not directly provided
        # This depends on how ConfigSectionProxy is obtained.
        # config = approve.config.config.sessions.blueski[user_id] # Example path
        pass # Needs actual way to get config proxy

    if not config:
        logger.error(f"Cannot process Blueski settings for user {user_id}: no config proxy available.")
        return False

    try:
        # Update the configuration values
        # await config.api_base_url.set(form.instance_url.data)
        await config.handle.set(form.handle.data)
        await config.app_password.set(form.app_password.data) # Ensure this is stored securely

        logger.info(f"Blueski settings updated for user {user_id}.")

        # If there's an active session, it might need to be reconfigured or restarted
        if session:
            logger.info(f"Requesting Blueski session re-initialization for user {user_id} due to settings change.")
            # await session.stop() # Stop it
            # # Update session instance with new values directly or rely on it re-reading config
            # session.api_base_url = form.instance_url.data
            # session.handle = form.handle.data
            # # App password should be handled carefully, session might need to re-login
            # await session.start() # Restart with new settings
            # Or, more simply, the session might have a reconfigure method:
            # await session.reconfigure(new_settings_dict)
            pass # Placeholder for session reconfiguration logic

        return True
    except Exception as e:
        logger.error(f"Error saving Blueski settings for user {user_id}: {e}", exc_info=True)
        return False

# Any additional Blueski-specific settings views or handlers would go here.
# For instance, if Blueski had features like "Relays" or "Feed Generators"
# that needed UI configuration within Approve, those forms and handlers could be defined here.

logger.info("Blueski settings module loaded (placeholders).")
