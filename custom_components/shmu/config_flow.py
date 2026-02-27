from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
from .const import DOMAIN

class SHMUConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle SHMU integration config flow."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user input for SHMU station configuration."""
        errors = {}
        if user_input is not None:
            # Validate user input
            if not user_input.get("station_id"):
                errors["station_id"] = "required"
            else:
                # Create config entry
                return self.async_create_entry(title=f"SHMU Station {user_input['station_id']}", data=user_input)

        # Show form to user
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("station_id", default="12345"): str,
                vol.Optional("scan_interval", default=300): int
            }),
            errors=errors
        )
