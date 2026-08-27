"""Select platform for Fancy LED (work mode, HDMI input)."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import FancyLedCoordinator
from .const import (
    CONF_DEVICE_ID,
    DOMAIN,
    DP_HDMI_INPUT,
    DP_HDMI_SYNC,
    DP_POWER,
    DP_SCENE_DATA,
    DP_SYNC_SENSITIVITY,
    DP_WORK_MODE,
    DEFAULT_SYNC_SENSITIVITY,
    HDMI_INPUT_OPTIONS,
    SCENE_MODES,
    SYNC_MODES,
    WORK_MODES,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: FancyLedCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FancyLedWorkModeSelect(coordinator, entry),
            FancyLedSceneSelect(coordinator, entry),
            FancyLedSyncModeSelect(coordinator, entry),
            FancyLedHdmiInputSelect(coordinator, entry),
        ]
    )


class _BaseSelect(CoordinatorEntity[FancyLedCoordinator], SelectEntity):
    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
            name=entry.data[CONF_NAME],
            manufacturer="FancyLEDs",
            model="HDMI Sync Box",
        )


class FancyLedWorkModeSelect(_BaseSelect):
    """Selects the device work mode: white / colour / scene / music."""

    _attr_options = WORK_MODES
    _attr_translation_key = "work_mode"

    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_work_mode"
        self._attr_name = f"{entry.data[CONF_NAME]} Work Mode"

    @property
    def current_option(self) -> str | None:
        return (self.coordinator.data or {}).get(DP_WORK_MODE)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_dp(DP_WORK_MODE, option)


class FancyLedHdmiInputSelect(_BaseSelect):
    """Selects the active HDMI input.

    NOTE: the raw values accepted by DP105 were not confirmed against real
    hardware. If your device reports/accepts different raw values, update
    HDMI_INPUT_OPTIONS in const.py to match (use the Raw DPS sensor to see
    the live value while switching inputs in the Fancyleds app).
    """

    _attr_translation_key = "hdmi_input"
    _attr_options = HDMI_INPUT_OPTIONS

    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_hdmi_input"
        self._attr_name = f"{entry.data[CONF_NAME]} HDMI Input"

    @property
    def current_option(self) -> str | None:
        value = (self.coordinator.data or {}).get(DP_HDMI_INPUT)
        return str(value) if value is not None else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_dp(DP_HDMI_INPUT, option)


class FancyLedSceneSelect(_BaseSelect):
    """Select one of the scene presets exposed by the FancyLEDs app."""

    _attr_options = list(SCENE_MODES)
    _payload_to_scene = {payload: name for name, payload in SCENE_MODES.items()}

    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_scene"
        self._attr_name = f"{entry.data[CONF_NAME]} Scene"

    @property
    def current_option(self) -> str | None:
        payload = (self.coordinator.data or {}).get(DP_SCENE_DATA)
        return self._payload_to_scene.get(payload)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_multiple(
            {
                DP_POWER: True,
                DP_WORK_MODE: "colour",
                DP_HDMI_SYNC: False,
                DP_SCENE_DATA: SCENE_MODES[option],
            }
        )


class FancyLedSyncModeSelect(_BaseSelect):
    """Select and enable a video-reactive HDMI Sync profile."""

    _attr_options = list(SYNC_MODES)
    _payload_to_mode = {payload: name for name, payload in SYNC_MODES.items()}

    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_sync_mode"
        self._attr_name = f"{entry.data[CONF_NAME]} Sync Mode"

    @property
    def current_option(self) -> str | None:
        payload = (self.coordinator.data or {}).get(DP_SCENE_DATA)
        return self._payload_to_mode.get(payload)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_multiple(
            {
                DP_POWER: True,
                DP_SCENE_DATA: SYNC_MODES[option],
                DP_SYNC_SENSITIVITY: DEFAULT_SYNC_SENSITIVITY,
                DP_HDMI_SYNC: True,
            }
        )
