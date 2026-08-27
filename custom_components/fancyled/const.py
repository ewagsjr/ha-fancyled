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
DP_COLOR_DATA = "24"     # hex string, 12-char Tuya HSV format (HHHHSSSSVVVV)
DP_SCENE_DATA = "25"     # scene string
DP_HDMI_INPUT = "105"    # enum, HDMI source select
DP_HDMI_SYNC = "107"     # bool, HDMI video-sync mode
DP_SYNC_SENSITIVITY = "108"  # int 0-1000, Sync diffusion/sensitivity

# DP109-113 exist on the device (CEC / HDR / colour
# enhancement per the app) but were NOT decoded in the upstream issue.
# They are intentionally NOT mapped to entities here - see the
# "Raw DPS" diagnostic sensor and the fancyled.set_raw_dp service for
# how to identify them on your own unit, then extend select.py/switch.py.
UNCONFIRMED_DPS = ["109", "110", "111", "112", "113"]

WORK_MODES = ["white", "colour", "scene", "music"]

# Verified against the 12 scene buttons in the FancyLEDs iOS app. Despite
# their UI label, these presets leave DP21 in "colour" and select the scene
# by writing the corresponding fixed payload to DP25.
SCENE_MODES = {
    "Rainbow": "86000000000000000000000000000000",
    "Fire": "87000000000000000000000000000000",
    "Calm": "88000000000000000000000000000000",
    "Fireworks": "89000000000000000000000000000000",
    "Star": "90000000000000000000000000000000",
    "Rain": "91000000000000000000000000000000",
    "Atom": "92000000000000000000000000000000",
    "Smooth": "93000000000000000000000000000000",
    "Bounce": "94000000000000000000000000000000",
    "Kinetic": "95000000000000000000000000000000",
    "Breathe": "96000000000000000000000000000000",
    "Color": "97000000000000000000000000000000",
}

# Sync profiles verified from the device's Tuya model and live hardware.
# The FancyLEDs app labels them Low, Medium, and High; upstream tuya-local
# calls the same DP25 payloads Movie, Leisure, and Gaming.
SYNC_MODES = {
    "Low": "80000000000000000000000000000000",
    "Medium": "81000000000000000000000000000000",
    "High": "82000000000000000000000000000000",
}
DEFAULT_SYNC_MODE = "High"
DEFAULT_SYNC_SENSITIVITY = 650

# Best-guess default; the box is advertised with 3 HDMI inputs. Verify
# against the Raw DPS sensor while switching inputs in the Fancyleds app
# and correct this list if your unit reports different raw values.
HDMI_INPUT_OPTIONS = ["0", "1", "2", "3"]
