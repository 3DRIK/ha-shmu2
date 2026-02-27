from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

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
            model="AWS Weather Station",
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

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the SHMU sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

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
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:compass",
        ),
    ]

    async_add_entities(sensors)
