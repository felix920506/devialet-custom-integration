"""Constants for the Devialet Custom integration."""

from datetime import timedelta

DOMAIN = "devialet_custom"
MANUFACTURER = "Devialet"

SCAN_INTERVAL = timedelta(seconds=10)

SOURCES = ["AES/EBU", "Analog", "Dante"]
