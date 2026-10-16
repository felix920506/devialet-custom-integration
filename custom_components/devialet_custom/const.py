"""Constants for the Devialet Custom integration."""

from datetime import timedelta

DOMAIN = "devialet_custom"
MANUFACTURER = "Devialet"

SCAN_INTERVAL = timedelta(seconds=10)

SOURCES = ["AES/EBU", "Analog", "Dante"]

CONF_SIMPLE_MODE = "simple_mode"

# Entity keys that are kept in simple mode; everything else is hidden.
SIMPLE_MODE_KEYS = ("media_player", "ledmode")

# Volume used to leave standby when nothing was saved and the startup
# volume is 0.
DEFAULT_ON_VOLUME = 50
