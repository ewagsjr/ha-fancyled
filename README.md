# Fancy LED (FancyLEDs HDMI Sync Box) for Home Assistant

A local-only Home Assistant custom integration for the **FancyLEDs HDMI sync box** (the ambient TV backlight strip controlled by the *Fancyleds* iOS/Android app). Communicates directly over your LAN using the Tuya local protocol (v3.4) — no cloud dependency after initial setup.

Polling uses a fresh local Tuya connection for each request so HA reports the
box's current state instead of queued updates from an older command. Partial
DPS responses are still merged defensively with the last complete state, and
successful writes are reflected optimistically until the next physical poll.

## Status

Core functionality (power, brightness, RGB color, color temperature, 12 app scene presets, three HDMI Sync modes, Sync sensitivity, work mode, and HDMI input) is implemented against the DPS map reverse-engineered in [make-all/tuya-local#3664](https://github.com/make-all/tuya-local/issues/3664) and verified against a live device. A handful of datapoints (DP109-113: CEC / HDR / color enhancement) are **not yet mapped** — see [Extending](#extending-unmapped-datapoints) below.

The scene presets, HDMI Sync modes, sensitivity control, color payload, and
non-persistent polling behavior were verified end-to-end on one protocol 3.4
FancyLEDs sync box. Please open an issue with results from other hardware revisions.

## Why local control instead of the Fancyleds app / Tuya cloud?

The device only ever speaks Tuya's protocol (it's a "Powered by Tuya" device; the Fancyleds app is a white-label skin on Tuya's SDK). This integration talks to it directly on your LAN using its `local_key`, so control keeps working even if your internet or Tuya's cloud is down. The Fancyleds app keeps working normally alongside this — nothing about the device's account binding changes.

## Getting your `local_key` and `device_id`

You need these once, from Tuya's IoT Cloud developer portal (this does **not** move your device out of the Fancyleds app or change how the app works):

1. Sign up at [iot.tuya.com](https://iot.tuya.com) using any account (can be separate from your Fancyleds login).
2. **Cloud → Create Cloud Project** → template "Smart Home" → pick the data center region matching where your Fancyleds account is registered.
3. Add the **Smart Home Basic Service** and **IoT Core** service to the project (you may be asked to select a free trial/subscription plan on a short form).
4. **Devices → Link App Account → Add App Account** → it shows a QR code.
5. Open the **Fancyleds app** on your phone → **Me** tab → tap the QR/scan icon in the corner → scan the code. This links read-only access; your app keeps working exactly as before.
6. Back in the portal: **Cloud → API Explorer → Devices Management → Query Device Details in Bulk** → paste your device ID (visible under Devices once linked) → the response includes `local_key`.

## Installation

### Via HACS (custom repository)

1. HACS → Integrations → ⋮ menu → **Custom repositories**.
2. Add this repo's URL, category **Integration**.
3. Install "Fancy LED (FancyLEDs HDMI Sync Box)", then restart Home Assistant.

### Manual

Copy `custom_components/fancyled` into your Home Assistant `config/custom_components/` folder, then restart.

## Setup

**Settings → Devices & Services → Add Integration → "Fancy LED"**, then enter:

| Field | Description |
|---|---|
| Name | Display name |
| IP address | The sync box's LAN IP (check your router's DHCP client list) |
| Device ID | From the Tuya IoT Cloud portal |
| Local key | From the Tuya IoT Cloud portal |
| Protocol version | `3.4` (try `3.3` if the connection test fails) |

## Entities

- **Light** — on/off, brightness, RGB color, color temperature (mode switches automatically between HS and color-temp based on the device's work mode)
- **Select: Work Mode** — white / colour / scene / music
- **Select: HDMI Input** — raw device options (`0`/`1`/`2`/`3`); verify against your unit (see below)
- **Select: Scene** — Rainbow / Fire / Calm / Fireworks / Star / Rain / Atom / Smooth / Bounce / Kinetic / Breathe / Color
- **Select: Sync Mode** — Low / Medium / High; selecting one enables Sync
- **Number: Sync Sensitivity** — 0–100%; defaults to 65% when Sync is enabled
- **Switch: HDMI Sync** — enables High Sync at 65% using DP25 + DP108 + DP107
- **Sensor: Raw DPS** (diagnostic) — every raw datapoint as attributes, for debugging and reverse-engineering

## Extending unmapped datapoints

DP109 through DP113 control CEC, HDR, and color-enhancement settings in the app, but their exact per-DP meanings have not been confirmed. To map them:

1. Watch the **Raw DPS** diagnostic sensor's attributes in Home Assistant's dev tools (Developer Tools → States).
2. Toggle one setting at a time in the Fancyleds app and note which DP number changes and what values it takes.
3. Add a `switch`/`select`/`number` entity for it in the corresponding platform file, following the pattern in `select.py`.
4. Send a PR.

There's also a diagnostic service, `fancyled.set_raw_dp`, for poking at a DP directly from Developer Tools → Actions while you experiment:

```yaml
action: fancyled.set_raw_dp
data:
  entry_id: <your config entry id>
  dp: "107"
  value: true
```

## License

MIT
