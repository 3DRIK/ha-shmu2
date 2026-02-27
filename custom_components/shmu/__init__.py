from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import async_timeout
import logging
from datetime import timedelta
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SHMU integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize coordinator
    coordinator = SHMUDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "camera"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, ["sensor", "camera"]):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class SHMUDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching SHMU data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the coordinator."""
        self._hass = hass
        self._entry = entry
        self._station_id = entry.data["station_id"]
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.data.get("scan_interval", 300)),
        )

    async def _async_update_data(self):
        """Fetch data from SHMU API."""
        try:
            async def _async_update_data(self):
    """Fetch data from SHMU API."""
    try:
        async with async_timeout.timeout(10):
            session = async_get_clientsession(self._hass)
            # Disable SSL verification (temporary workaround)
            connector = aiohttp.TCPConnector(ssl=False)
            async with session.get(
                f"https://opendata.shmu.sk/meteorology/climate/now/data/{self._station_id}.json",
                connector=connector,
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching SHMU data: {response.status}")
                return await response.json()
    except Exception as err:
        raise UpdateFailed(f"Error communicating with SHMU API: {err}")
