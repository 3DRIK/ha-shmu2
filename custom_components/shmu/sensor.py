from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from datetime import datetime, timedelta
from .const import DOMAIN
from homeassistant.util.dt import now

# Warning types
WARNING_TYPES = [
    "Búrka",
    "Dážď",
    "Hmla",
    "Poľadovica",
    "Mráz vo vegetačnom období",
    "Sneženie",
    "Teploty nízke",
    "Teploty vysoké",
    "Vietor",
    "Záveje",
    "Vietor na horách",
]

class SHMUWarningSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SHMU warning sensor for a specific warning type in a city."""

    def __init__(self, coordinator, city, warning_type):
        """Initialize the warning sensor."""
        super().__init__(coordinator)
        self._city = city
        self._warning_type = warning_type
        self._attr_name = f"{city} {warning_type}"
        self._attr_unique_id = f"{DOMAIN}_{city}_{warning_type}_{coordinator.config_entry.entry_id}"
        self._attr_icon = self._get_icon_for_warning_type(warning_type)
        self._attr_device_info = DeviceInfo(
            identifiers={(f"{DOMAIN}_{city}", coordinator.config_entry.entry_id)},
            name=f"SHMU Warnings for {city}",
            manufacturer="Slovenský hydrometeorologický ústav",
            model="Warning System",
        )

    def _get_icon_for_warning_type(self, warning_type):
        """Return an appropriate icon for the warning type."""
        icons = {
            "Búrka": "mdi:weather-lightning",
            "Dážď": "mdi:weather-pouring",
            "Hmla": "mdi:weather-fog",
            "Poľadovica": "mdi:weather-snowy-rainy",
            "Mráz vo vegetačnom období": "mdi:snowflake-thermometer",
            "Sneženie": "mdi:weather-snowy",
            "Teploty nízke": "mdi:thermometer-low",
            "Teploty vysoké": "mdi:thermometer-high",
            "Vietor": "mdi:weather-windy",
            "Záveje": "mdi:weather-snowy-heavy",
            "Vietor na horách": "mdi:weather-windy-variant",
        }
        return icons.get(warning_type, "mdi:alert")

    async def async_update(self):
        """Fetch the latest warning data."""
        self._attr_available = True
        warnings = await self._async_fetch_warnings()
        active_warning = warnings.get(self._city, {}).get(self._warning_type)
        if active_warning:
            self._attr_native_value = "Active"
            self._attr_extra_state_attributes = {
                "description": active_warning.get("description"),
                "start": active_warning.get("start"),
                "end": active_warning.get("end"),
            }
        else:
            self._attr_native_value = "Inactive"
            self._attr_extra_state_attributes = {}

    async def _async_fetch_warnings(self):
        """Fetch warnings for all cities (placeholder function)."""
        # Replace this with actual API call to SHMU warnings
        return {
            "Bratislava": {
                "Búrka": {
                    "description": "Strong thunderstorms expected",
                    "start": datetime.now().isoformat(),
                    "end": (datetime.now() + timedelta(hours=6)).isoformat(),
                },
            },
            "Košice": {
                "Vietor": {
                    "description": "Strong winds expected",
                    "start": datetime.now().isoformat(),
                    "end": (datetime.now() + timedelta(hours=6)).isoformat(),
                },
            },
        }
        
class SHMUSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SHMU sensor."""

    def __init__(
        self,
        coordinator,
        sensor_key: str,
        name: str,
        unit: str,
        device_class: SensorDeviceClass = None,
        icon: str = None,
        state_class: SensorStateClass = None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._name = name
        self._unit = unit
        self._device_class = device_class
        self._icon = icon
        self._state_class = state_class
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{sensor_key}"

        # Dynamic device name based on station_id
        station_id = coordinator.config_entry.data["station_id"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"SHMU Station {station_id}",
            manufacturer="Slovenský hydrometeorologický ústav",
            model="Weather Station",
            sw_version="1.0",
        )

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._attr_unique_id

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_key)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement as a string."""
        return self._unit

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class."""
        return self._device_class

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class."""
        return self._state_class

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._icon


class SHMUMeteogramSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SHMU meteogram URL sensor."""

    def __init__(self, coordinator, meteogram_id=None):
        """Initialize the meteogram URL sensor."""
        super().__init__(coordinator)
        self._attr_name = "SHMU Meteogram URL"
        self._attr_unique_id = f"{DOMAIN}_meteogram_url_{coordinator.config_entry.entry_id}"
        self._attr_icon = "mdi:image"
        self._meteogram_id = meteogram_id or "32737"  # Default meteogram ID

        # Dynamic device name based on station_id
        station_id = coordinator.config_entry.data["station_id"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"SHMU Station {station_id}",
            manufacturer="Slovenský hydrometeorologický ústav",
            model="Weather Station",
            sw_version="1.0",
        )

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
        return f"https://www.shmu.sk/data/datanwp/v2/meteogram/al-meteogram_{self._meteogram_id}-{date}-{time}-nwp-.png"

    @property
    def native_value(self):
        """Return the meteogram URL."""
        return "Meteogram URL"

    @property
    def extra_state_attributes(self):
        """Return the attributes for the meteogram URL."""
        return {"meteogram_url": self._generate_meteogram_url()}

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the SHMU sensors."""

    config_type = config_entry.domain.split("_")[-1] if "_" in config_entry.domain else "station"

    if config_type == "station":
        coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
        meteogram_id = coordinator.config_entry.data.get("meteogram_id", "none")
        sensors = [
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="t",
                name="Temperature",
                unit="°C",
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:thermometer",
            ),
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="vlh_rel",
                name="Humidity",
                unit=PERCENTAGE,
                device_class=SensorDeviceClass.HUMIDITY,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:water-percent",
            ),
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="tlak",
                name="Pressure",
                unit="hPa",
                device_class=SensorDeviceClass.PRESSURE,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:gauge",
            ),
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="vie_pr_rych",
                name="Wind Speed",
                unit="m/s",
                device_class=SensorDeviceClass.WIND_SPEED,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:weather-windy",
            ),
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="vie_pr_smer",
                name="Wind Direction",
                unit="°",
                device_class=None,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:compass",
            ),
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="sln_trv",
                name="Sun duration/min",
                unit="sec",
                device_class=None,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:sun-clock",
            ),
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="zglo",
                name="Global radiation",
                unit="W/m²",
                device_class=None,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:sun-wireless",
            ),
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="zra_trv",
                name="Precipitation duration",
                unit="sec",
                device_class=None,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:weather-rainy",
            ),
            SHMUSensor(
                coordinator=coordinator,
                sensor_key="zra_uhrn",
                name="Precipitation volume",
                unit="mm",
                device_class=None,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:cup-water",
            )]
        # Only add the meteogram sensor if meteogram_id is not "none"
        if meteogram_id != "none":
            sensors.append(SHMUMeteogramSensor(coordinator, meteogram_id))

        async_add_entities(sensors)
    elif config_type == "warnings":
        coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
        cities = config_entry.data.get("cities", [])

        # Get existing devices from device registry
        device_registry = dr.async_get(hass)
        existing_cities = set()
        for device in device_registry.devices.values():
            if device.identifiers and any(identifier[0].startswith(f"{DOMAIN}_") for identifier in device.identifiers):
                for identifier in device.identifiers:
                    if identifier[0].startswith(f"{DOMAIN}_"):
                        city = identifier[0].split("_", 2)[1]
                        if city in CITIES:
                            existing_cities.add(city)


        # Add warning sensors for each selected city and warning type, but only if the city is not already set up
        sensors = []
        for city in cities:
            if city not in existing_cities:
                for warning_type in WARNING_TYPES:
                    sensors.append(SHMUWarningSensor(coordinator, city, warning_type))
        async_add_entities(sensors)

                    
