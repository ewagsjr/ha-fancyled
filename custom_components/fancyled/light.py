"""Light platform for Fancy LED."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
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
    DP_BRIGHTNESS,
    DP_COLOR_DATA,
    DP_COLOR_TEMP,
    DP_POWER,
    DP_WORK_MODE,
)

_LOGGER = logging.getLogger(__name__)

MIN_KELVIN = 2700
MAX_KELVIN = 6500

# Tuya "colour_data_v2" DP format: 6 hex RGB + 4 hex H(0-360) + 4 hex S(0-1000) + 4 hex V(0-1000)
def _decode_color(raw: str) -> tuple[float, float]:
    """Return (hue 0-360, saturation 0-100) from a colour_data_v2 hex string."""
    h = int(raw[6:10], 16)
    s = int(raw[10:14], 16)
    return (float(h), s / 10.0)


def _encode_color(hue: float, saturation: float, value: int) -> str:
    """Build a colour_data_v2 hex string from HSV (h 0-360, s 0-100, v 0-1000)."""
    import colorsys

    r, g, b = colorsys.hsv_to_rgb(hue / 360, saturation / 100, 1.0)
    rgb_hex = f"{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    h_hex = f"{int(hue):04x}"
    s_hex = f"{int(saturation * 10):04x}"
    v_hex = f"{int(value):04x}"
    return rgb_hex + h_hex + s_hex + v_hex


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: FancyLedCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FancyLedLight(coordinator, entry)])


class FancyLedLight(CoordinatorEntity[FancyLedCoordinator], LightEntity):
    """The main light entity for the Fancy LED sync box strip."""

    _attr_supported_color_modes = {ColorMode.HS, ColorMode.COLOR_TEMP}
    _attr_min_color_temp_kelvin = MIN_KELVIN
    _attr_max_color_temp_kelvin = MAX_KELVIN

    def __init__(self, coordinator: FancyLedCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_light"
        self._attr_name = entry.data[CONF_NAME]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
            name=entry.data[CONF_NAME],
            manufacturer="FancyLEDs",
            model="HDMI Sync Box",
        )

    @property
    def _dps(self) -> dict:
        return self.coordinator.data or {}

    @property
    def is_on(self) -> bool:
        return bool(self._dps.get(DP_POWER, False))

    @property
    def brightness(self) -> int:
        raw = self._dps.get(DP_BRIGHTNESS, 10)
        return round((raw - 10) / (1000 - 10) * 255)

    @property
    def color_mode(self) -> ColorMode:
        return (
            ColorMode.COLOR_TEMP
            if self._dps.get(DP_WORK_MODE) == "white"
            else ColorMode.HS
        )

    @property
    def hs_color(self) -> tuple[float, float] | None:
        raw = self._dps.get(DP_COLOR_DATA)
        if not raw or len(raw) < 14:
            return None
        return _decode_color(raw)

    @property
    def color_temp_kelvin(self) -> int | None:
        raw = self._dps.get(DP_COLOR_TEMP)
        if raw is None:
            return None
        ratio = raw / 1000
        return round(MIN_KELVIN + ratio * (MAX_KELVIN - MIN_KELVIN))

    async def async_turn_on(self, **kwargs: Any) -> None:
        values: dict[str, Any] = {DP_POWER: True}

        if "brightness" in kwargs:
            values[DP_BRIGHTNESS] = round(10 + kwargs["brightness"] / 255 * (1000 - 10))

        if "hs_color" in kwargs:
            hue, sat = kwargs["hs_color"]
            v_scale = self._dps.get(DP_BRIGHTNESS, 1000)
            values[DP_WORK_MODE] = "colour"
            values[DP_COLOR_DATA] = _encode_color(hue, sat, v_scale)

        if "color_temp_kelvin" in kwargs:
            kelvin = kwargs["color_temp_kelvin"]
            ratio = (kelvin - MIN_KELVIN) / (MAX_KELVIN - MIN_KELVIN)
            values[DP_WORK_MODE] = "white"
            values[DP_COLOR_TEMP] = round(max(0, min(1, ratio)) * 1000)

        await self.coordinator.async_set_multiple(values)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_dp(DP_POWER, False)
