"""Number platform for Fancy LED Sync sensitivity."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import FancyLedCoordinator
from .const import CONF_DEVICE_ID, DOMAIN, DP_SYNC_SENSITIVITY


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Sync sensitivity control."""
    coordinator: FancyLedCoordinator = hass.data[DOMAIN][entry.entry_id]
    if DP_SYNC_SENSITIVITY in (coordinator.data or {}):
        async_add_entities([FancyLedSyncSensitivityNumber(coordinator, entry)])


class FancyLedSyncSensitivityNumber(
    CoordinatorEntity[FancyLedCoordinator], NumberEntity
):
    """Control HDMI Sync sensitivity/diffusion as a percentage."""

    _attr_icon = "mdi:blur"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_sync_sensitivity"
        self._attr_name = f"{entry.data[CONF_NAME]} Sync Sensitivity"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
            name=entry.data[CONF_NAME],
            manufacturer="FancyLEDs",
            model="HDMI Sync Box",
        )

    @property
    def native_value(self) -> float | None:
        value = (self.coordinator.data or {}).get(DP_SYNC_SENSITIVITY)
        return round(value / 10, 1) if isinstance(value, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_dp(DP_SYNC_SENSITIVITY, round(value * 10))
