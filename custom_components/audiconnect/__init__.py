"""The Audi connect integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .coordinator import AudiDataUpdateCoordinator
from .services import async_setup_services

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SWITCH,
    Platform.LOCK,
    # Platform.SELECT,
    Platform.NUMBER,
]

type AudiConfigEntry = ConfigEntry[AudiDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AudiConfigEntry) -> bool:
    """Set up Audi connect from a config entry."""
    coordinator = AudiDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass, coordinator)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Reload device tracker if change option."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove config entry from a device."""
    return True
