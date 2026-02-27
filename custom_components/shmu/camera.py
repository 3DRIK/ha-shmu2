from homeassistant.components.camera import Camera
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from datetime import datetime, timedelta
from .const import DOMAIN
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

class SHMUMeteogramCamera(CoordinatorEntity, Camera):
    """Representation of a SHMU meteogram camera."""

    def __init__(self, coordinator):
        """Initialize the meteogram camera."""
        super().__init__(coordinator)
        self._attr_name = "SHMU Meteogram"
        self._attr_unique_id = f"{DOMAIN}_meteogram_{coordinator.config_entry.entry_id}"
        self._access_tokens = set()  # Required for camera authentication

        # Dynamic device name based on station_id
        station_id = coordinator.config_entry.data["station_id"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"SHMU Station {station_id}",
            manufacturer="Slovenský hydrometeorologický ústav",
            model="AWS Weather Station",
            sw_version="1.0",
        )

    @property
    def access_tokens(self):
        """Return the access tokens."""
        return self._access_tokens

    def _generate_meteogram_url(self):
        """Generate the meteogram URL based on current time."""
        now = datetime.now()
        if now.hour < 6:
            date = (now - timedelta(days=1)).strftime("%Y%m%d")
            time = "1600"
        elif now.hour < 12:
            date = now.strftime("%Y%m%d")
            time = "0000"
        elif now.hour < 17:
            date = now.strftime("%Y%m%d")
            time = "0600"
        else:
            date = now.strftime("%Y%m%d")
            time = "1200"
        return f"https://www.shmu.sk/data/datanwp/v2/meteogram/al-meteogram_32737-{date}-{time}-nwp-.png"

    async def async_camera_image(self, width=None, height=None):
        """Return the meteogram image."""
        url = self._generate_meteogram_url()
        _LOGGER.debug("Fetching meteogram from URL: %s", url)

        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            _LOGGER.error("Error fetching meteogram: HTTP %s", response.status)
                            return None
                        return await response.read()
        except Exception as err:
            _LOGGER.error("Error fetching meteogram: %s", err)
            return None

    async def handle_async_mjpeg_stream(self, request):
        """Generate an HTTP MJPEG stream from the camera."""
        return None

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the SHMU meteogram camera."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    camera = SHMUMeteogramCamera(coordinator)
    async_add_entities([camera])
    _LOGGER.debug("SHMU Meteogram camera setup complete")
