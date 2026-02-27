from homeassistant.components.camera import Camera
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class SHMUMeteogramCamera(CoordinatorEntity, Camera):
    """Representation of a SHMU meteogram camera."""

    def __init__(self, coordinator):
        """Initialize the meteogram camera."""
        super().__init__(coordinator)
        self._attr_name = "SHMU Meteogram"
        self._attr_unique_id = f"{DOMAIN}_meteogram_{coordinator.config_entry.entry_id}"

    async def async_camera_image(self):
        """Return the meteogram image."""
        url = self._generate_meteogram_url()
        return await self._fetch_image(url)

    def _generate_meteogram_url(self):
        """Generate the meteogram URL based on current time."""
        from datetime import datetime
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

    async def _fetch_image(self, url):
        """Fetch the image from the URL."""
        session = async_get_clientsession(self.hass)
        response = await session.get(url)
        return await response.read()
