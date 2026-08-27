"""Switch platform for Fancy LED HDMI video sync."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import FancyLedCoordinator
from .const import (
    CONF_DEVICE_ID,
    DEFAULT_SYNC_MODE,
    DEFAULT_SYNC_SENSITIVITY,
    DOMAIN,
    DP_HDMI_SYNC,
    DP_POWER,
    DP_SCENE_DATA,
    DP_SYNC_SENSITIVITY,
    SYNC_MODES,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up HDMI sync when the device advertises its datapoint."""
    coordinator: FancyLedCoordinator = hass.data[DOMAIN][entry.entry_id]
    if DP_HDMI_SYNC in (coordinator.data or {}):
        async_add_entities([FancyLedHdmiSyncSwitch(coordinator, entry)])


class FancyLedHdmiSyncSwitch(
    CoordinatorEntity[FancyLedCoordinator], SwitchEntity
):
    """Enable or disable HDMI video-reactive lighting."""

    _attr_icon = "mdi:television-ambient-light"

    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_hdmi_sync"
        self._attr_name = f"{entry.data[CONF_NAME]} HDMI Sync"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
            name=entry.data[CONF_NAME],
            manufacturer="FancyLEDs",
            model="HDMI Sync Box",
        )

    @property
    def is_on(self) -> bool:
        return bool((self.coordinator.data or {}).get(DP_HDMI_SYNC, False))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_multiple(
            {
                DP_POWER: True,
                DP_SCENE_DATA: SYNC_MODES[DEFAULT_SYNC_MODE],
                DP_SYNC_SENSITIVITY: DEFAULT_SYNC_SENSITIVITY,
                DP_HDMI_SYNC: True,
            }
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_dp(DP_HDMI_SYNC, False)
