from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
from homeassistant.helpers import config_validation as cv, device_registry as dr
from .const import DOMAIN

# List of cities for warnings
CITIES = [
    "Bratislava",
    "Košice",
    "Žilina",
    "Banská Bystrica",
    "Nitra",
    "Trnava",
    "Trenčín",
    "Prešov",
]

class SHMUStationConfigFlow(config_entries.ConfigFlow, domain=f"{DOMAIN}_station"):
    """Handle a config flow for SHMU Station."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step for SHMU Station."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=f"SHMU Station {user_input['station_id']}",
                data={
                    "station_id": user_input["station_id"],
                    "meteogram_id": user_input["meteogram_id"],
                    "scan_interval": user_input["scan_interval"],
                    "verify_ssl": user_input["verify_ssl"],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("station_id", default="11813"): str,
                    vol.Optional("meteogram_id", default="32737"): str,
                    vol.Optional("scan_interval", default=300): int,
                    vol.Optional("verify_ssl", default=True): bool,
                }
            ),
            errors=errors,
        )

class SHMUWarningsConfigFlow(config_entries.ConfigFlow, domain=f"{DOMAIN}_warnings"):
    """Handle a config flow for SHMU Warnings."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step for SHMU Warnings."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="SHMU Warnings",
                data={
                    "cities": user_input.get("cities", []),
                },
            )

        # Get existing cities from device registry
        device_registry = dr.async_get(self.hass)
        existing_cities = []
        for device in device_registry.devices.values():
            if device.identifiers and any(identifier[0].startswith(f"{DOMAIN}_") for identifier in device.identifiers):
                for identifier in device.identifiers:
                    if identifier[0].startswith(f"{DOMAIN}_"):
                        city = identifier[0].split("_", 2)[1]
                        if city in CITIES and city not in existing_cities:
                            existing_cities.append(city)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional("cities", default=existing_cities): cv.multi_select(CITIES),
                }
            ),
            errors=errors,
        )

@config_entries.HANDLERS.register(DOMAIN)
class SHMUConfigFlowHandler:
    """Handle a config flow for SHMU."""

    def __init__(self):
        """Initialize the config flow handler."""
        self.station_flow = SHMUStationConfigFlow()
        self.warnings_flow = SHMUWarningsConfigFlow()

    async def async_step_import(self, import_info):
        """Handle import from configuration.yaml."""
        return await self.station_flow.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle the initial step by showing a menu."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["station", "warnings"],
        )

    async def async_step_station(self, user_input=None):
        """Forward to station config flow."""
        return await self.station_flow.async_step_user(user_input)

    async def async_step_warnings(self, user_input=None):
        """Forward to warnings config flow."""
        return await self.warnings_flow.async_step_user(user_input)
