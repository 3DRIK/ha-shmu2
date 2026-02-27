from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE, PRESSURE_HPA, SPEED_METERS_PER_SECOND, DEGREE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class SHMUSensor(CoordinatorEntity, SensorEntity):
    """Base class for SHMU sensors."""

    def __init__(self, coordinator, sensor_key, name, unit, device_class=None):
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._name = name
        self._unit = unit
        self._device_class = device_class
        self._unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{sensor_key}"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.coordinator.data.get(self._sensor_key)

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def device_class(self):
        return self._device_class

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors for SHMU integration."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    sensors = [
        SHMUSensor(coordinator, "t", "Temperature", TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE),
        SHMUSensor(coordinator, "vlh_rel", "Humidity", PERCENTAGE, SensorDeviceClass.HUMIDITY),
        SHMUSensor(coordinator, "tlak", "Pressure", PRESSURE_HPA, SensorDeviceClass.PRESSURE),
        SHMUSensor(coordinator, "vie_pr_rych", "Wind Speed", SPEED_METERS_PER_SECOND),
        SHMUSensor(coordinator, "vie_pr_smer", "Wind Direction", DEGREE)
    ]
    async_add_entities(sensors)
