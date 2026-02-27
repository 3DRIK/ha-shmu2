from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfSpeed,
)
from .const import DOMAIN

class SHMUSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SHMU sensor."""

    def __init__(
        self,
        coordinator,
        sensor_key: str,
        name: str,
        unit: str,  # Changed from UnitType to str
        device_class: SensorDeviceClass = None,
        icon: str = None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._name = name
        self._unit = unit
        self._device_class = device_class
        self._icon = icon
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{sensor_key}"

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
    def native_unit_of_measurement(self) -> str:  # Changed return type to str
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class."""
        return self._device_class

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
            name="SHMU Temperature",
            unit=UnitOfTemperature.CELSIUS,  # Still valid
            device_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
        ),
        SHMUSensor(
            coordinator=coordinator,
            sensor_key="vlh_rel",
            name="SHMU Humidity",
            unit=PERCENTAGE,  # Still valid
            device_class=SensorDeviceClass.HUMIDITY,
            icon="mdi:water-percent",
        ),
        SHMUSensor(
            coordinator=coordinator,
            sensor_key="tlak",
            name="SHMU Pressure",
            unit=UnitOfPressure.HPA,  # Still valid
            device_class=SensorDeviceClass.PRESSURE,
            icon="mdi:gauge",
        ),
        SHMUSensor(
            coordinator=coordinator,
            sensor_key="vie_pr_rych",
            name="SHMU Wind Speed",
            unit=UnitOfSpeed.METERS_PER_SECOND,  # Still valid
            device_class=SensorDeviceClass.WIND_SPEED,
            icon="mdi:weather-windy",
        ),
        SHMUSensor(
            coordinator=coordinator,
            sensor_key="vie_pr_smer",
            name="SHMU Wind Direction",
            unit="°",  # Changed from UnitType.DEGREE to string
            device_class=SensorDeviceClass.WIND_SPEED,
            icon="mdi:compass",
        ),
    ]

    async_add_entities(sensors)
