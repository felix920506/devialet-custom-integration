# Devialet Custom for Home Assistant

A Home Assistant integration for **Devialet Custom** speakers (e.g. *Phantom Reactor Custom*): the stripped-down units sold to integrators that only offer wired sources (AES/EBU, Analog, Dante) and a plain HTTP configuration page. The official Devialet integration doesn't work with them because they lack the regular IP Control API.

This integration talks to the same local HTTP API the speaker's configuration page uses. It needs no cloud access and no extra Python dependencies.

## Features

| Entity | Type | Notes |
| --- | --- | --- |
| Speaker | `media_player` | Volume, mute, input source (AES/EBU / Analog / Dante) |
| Startup volume | `number` | 0–100 % |
| Max SPL | `number` | 50–96 dB |
| Analog sensitivity | `number` | 1–10 Vrms, 0.5 steps |
| LED mode | `select` | Off / On / Slow blinking / Fast blinking |
| Channel mix | `select` | Left / Right / Mono mix |
| Startup source | `select` | AES/EBU / Analog / Dante |
| Source state, stream type, internal state | `sensor` | Diagnostic |
| ASIC / amplifier / SoC temperature | `sensor` | Diagnostic |

The speaker is polled every 10 seconds.

## Installation

### HACS

1. In HACS, open the menu → **Custom repositories**.
2. Add `https://github.com/felix920506/devialet-custom-integration` with category **Integration**.
3. Install **Devialet Custom** and restart Home Assistant.

### Manual

Copy `custom_components/devialet_custom` into your Home Assistant `config/custom_components/` directory and restart.

## Setup

**Settings → Devices & services → Add integration → Devialet Custom**, then enter the speaker's IP address. Add each speaker separately. Speakers are identified by serial number, so if one changes IP you can re-add it and the existing entry will be updated.

Give your speakers static DHCP leases so their addresses don't change.

## API reference

These are the endpoints the integration uses, as served by the speaker's configuration web app (firmware 1.1.2):

| Method | Path | Body / response |
| --- | --- | --- |
| `GET` | `/device/info` | `{"data": {"model", "serial", "release": {"version"}, ...}}` |
| `GET` | `/cisettings/getall` | `{"data": {...all settings...}}` |
| `GET` | `/cisettings/<key>` | `{"data": {"<key>": value}}` |
| `POST` | `/cisettings/<key>` | `{"<key>": value}` → `{}` on success, `{"error": {"code", "message"}}` on failure (still HTTP 200) |

## Disclaimer

This is an unofficial project and isn't affiliated with or endorsed by Devialet.
