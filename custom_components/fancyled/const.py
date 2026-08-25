"""Constants for the Fancy LED (FancyLEDs HDMI Sync Box) integration."""

DOMAIN = "fancyled"

CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_PROTOCOL_VERSION = "protocol_version"

DEFAULT_PROTOCOL_VERSION = "3.4"
DEFAULT_NAME = "Fancy LED"
DEFAULT_PORT = 6668

UPDATE_INTERVAL_SECONDS = 10

# --- Confirmed DPS map, from community reverse-engineering of the
# FancyLEDs 2.0 / 3 HDMI sync box (Tuya product id 9cgdcqpe9iqg9tjn).
# See: https://github.com/make-all/tuya-local/issues/3664
DP_POWER = "20"          # bool
DP_WORK_MODE = "21"      # enum: white / colour / scene / music
DP_BRIGHTNESS = "22"     # int 10-1000
DP_COLOR_TEMP = "23"     # int 0-1000 (only meaningful in "white" work mode)
DP_COLOR_DATA = "24"     # hex string, Tuya colour_data_v2 format (18 hex chars)
DP_SCENE_DATA = "25"     # scene string
DP_HDMI_INPUT = "105"    # enum, HDMI source select

# DP107-113 exist on the device (sensitivity / HDR / TV-sync / colour
# enhancement per the app) but were NOT decoded in the upstream issue.
# They are intentionally NOT mapped to entities here - see the
# "Raw DPS" diagnostic sensor and the fancyled.set_raw_dp service for
# how to identify them on your own unit, then extend select.py/switch.py.
UNCONFIRMED_DPS = ["107", "108", "109", "110", "111", "112", "113"]

WORK_MODES = ["white", "colour", "scene", "music"]

# Best-guess default; the box is advertised with 3 HDMI inputs. Verify
# against the Raw DPS sensor while switching inputs in the Fancyleds app
# and correct this list if your unit reports different raw values.
HDMI_INPUT_OPTIONS = ["1", "2", "3"]
