"""Diagnostic sensor exposing every raw DPS value.

This exists so you can reverse-engineer the unconfirmed datapoints
(DP107-113: sensitivity / HDR / TV-sync / colour enhancement per the
FancyLEDs app). Watch this entity's attributes while toggling each
setting in the app, note which DP number changes and what values it
takes, then add a proper select/switch/number entity for it.
"""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import FancyLedCoordinator
from .const import CONF_DEVICE_ID, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: FancyLedCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FancyLedRawDpsSensor(coordinator, entry)])


class FancyLedRawDpsSensor(CoordinatorEntity[FancyLedCoordinator], SensorEntity):
    """Shows the count of known DPS, with the full raw map as attributes."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "raw_dps"

    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_raw_dps"
        self._attr_name = f"{entry.data[CONF_NAME]} Raw DPS"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
            name=entry.data[CONF_NAME],
            manufacturer="FancyLEDs",
            model="HDMI Sync Box",
        )

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict:
        return dict(self.coordinator.data or {})
