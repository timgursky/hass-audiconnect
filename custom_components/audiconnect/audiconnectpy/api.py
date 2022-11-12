"""Audi connect."""
from __future__ import annotations

import asyncio
import logging
import time

from .auth import Auth
from .models import Vehicle
from .services import AudiService
from .exceptions import HttpRequestError, RequestError


_LOGGER = logging.getLogger(__name__)

MAX_RESPONSE_ATTEMPTS = 10
REQUEST_STATUS_SLEEP = 5

ACTION_LOCK = "lock"
ACTION_CLIMATISATION = "climatisation"
ACTION_CHARGER = "charger"
ACTION_WINDOW_HEATING = "window_heating"
ACTION_PRE_HEATER = "pre_heater"


class AudiConnect:
    """Representation of an Audi Connect Account."""

    def __init__(
        self, session, username: str, password: str, country: str, spin: str
    ) -> None:
        """Initiliaze."""
        self._api = Auth(session)
        self._audi_service = AudiService(self._api, country, spin)
        self._username = username
        self._password = password
        self._logintime = time.time()
        self._connect_retries = 3
        self._connect_delay = 10
        self._audi_vehicles: list[Vehicle] = []
        self._excluded_refresh: set[str] = set()
        self.is_connected = False
        self.vehicles: dict[str, Vehicle] = {}

    async def async_login(self, ntries=3) -> bool:
        """Login and retreive tokens."""
        if not self.is_connected:
            try:
                await self._audi_service.async_login_request(
                    self._username, self._password
                )
            except HttpRequestError as error:  # pylint: disable=broad-except
                if ntries > 1:
                    _LOGGER.error(
                        "Login to Audi service failed, trying again in %s seconds",
                        self._connect_delay,
                    )
                    await asyncio.sleep(self._connect_delay)
                    await self.async_login(ntries - 1)
                else:
                    _LOGGER.error("Login to Audi service failed: %s ", str(error))
                    self.is_connected = False
            else:
                self.is_connected = True
                self._logintime = time.time()
        return self.is_connected

    async def async_update(self, vinlist: list[str] | None = None) -> bool:
        """Update data."""
        if not await self.async_login():
            return False

        elapsed_sec = time.time() - self._logintime
        if await self._audi_service.async_refresh_token_if_necessary(elapsed_sec):
            # Store current timestamp when refresh was performed and successful
            self._logintime = time.time()

        # Update the state of all vehicles.
        try:
            if len(self._audi_vehicles) > 0:
                for vehicle in self._audi_vehicles:
                    await self.async_add_or_update_vehicle(vehicle, vinlist)

            else:
                vehicles_response = (
                    await self._audi_service.async_get_vehicle_information()
                )
                for response in vehicles_response.get("userVehicles"):
                    self._audi_vehicles.append(Vehicle(response, self._audi_service))

                self.vehicles = {}
                for vehicle in self._audi_vehicles:
                    await self.async_add_or_update_vehicle(vehicle, vinlist)

            return True

        except IOError as exception:
            # Force a re-login in case of failure/exception
            self.is_connected = False
            _LOGGER.exception(exception)
            return False

    async def async_add_or_update_vehicle(
        self, vehicle, vinlist: list[str] | None
    ) -> None:
        """Add or Update vehicle."""
        if vehicle.vin is not None:
            if vinlist is None or vehicle.vin.lower() in vinlist:
                vupd = [
                    x for vin, x in self.vehicles.items() if vin == vehicle.vin.lower()
                ]
                if len(vupd) > 0:
                    if await vupd[0].async_fetch_data(self._connect_retries) is False:
                        self.is_connected = False
                else:
                    try:
                        if (
                            await vehicle.async_fetch_data(self._connect_retries)
                            is False
                        ):
                            self.is_connected = False
                        self.vehicles.update({vehicle.vin: vehicle})
                    except Exception:  # pylint: disable=broad-except
                        pass

    async def async_refresh_vehicle_data(self, vin: str) -> bool:
        """Refresh vehicle data."""
        if not await self.async_login():
            return False

        try:
            if vin not in self._excluded_refresh:
                _LOGGER.debug("Sending command to refresh data to vehicle %s", vin)
                await self._audi_service.async_refresh_vehicle_data(vin)
                _LOGGER.debug("Successfully refreshed data of vehicle %s", vin)
                return True
        except RequestError as error:
            if error.status in (403, 502):
                _LOGGER.debug("refresh vehicle not supported: %s", error.status)
                self._excluded_refresh.add(vin)
            else:
                _LOGGER.error(
                    "Unable to refresh vehicle data of %s: %s",
                    vin,
                    str(error).rstrip("\n"),
                )
        except HttpRequestError as error:  # pylint: disable=broad-except
            _LOGGER.error(
                "Unable to refresh vehicle data of %s: %s", vin, str(error).rstrip("\n")
            )
        return False

    async def async_refresh_vehicles(self) -> bool:
        """Refresh all vehicles data."""
        if not await self.async_login():
            return False

        for vin in self.vehicles:
            await self.async_refresh_vehicle_data(vin)

        return True

    async def async_set_lock(self, vin: str, lock: bool) -> bool:
        """Set lock."""
        if not await self.async_login():
            return False

        try:
            action = "lock" if lock else "unlock"
            _LOGGER.debug("Sending command to %s to vehicle %s", action, vin)
            await self._audi_service.async_set_lock(vin, lock)
            action = "locked" if lock else "unlocked"
            _LOGGER.debug("Successfully %s vehicle %s", action, vin)
            return True
        except RequestError as error:  # pylint: disable=broad-except
            _LOGGER.error(
                "Unable to %s %s: %s",
                action,
                vin,
                str(error).rstrip("\n"),
            )
            return False

    async def async_set_climatisation(self, vin: str, activate: bool) -> bool:
        """Set climatisation."""
        if not await self.async_login():
            return False

        try:
            action = "start" if activate else "stop"
            _LOGGER.debug(
                "Sending command to %s climatisation to vehicle %s", action, vin
            )
            await self._audi_service.async_set_climatisation(vin, activate)
            action = "started" if activate else "stopped"
            _LOGGER.debug("Successfully %s climatisation of vehicle %s", action, vin)
            return True
        except RequestError as error:  # pylint: disable=broad-except
            _LOGGER.error(
                "Unable to %s climatisation of vehicle %s: %s",
                action,
                vin,
                str(error).rstrip("\n"),
            )
            return False

    async def async_set_battery_charger(
        self, vin: str, activate: bool, timer: str
    ) -> bool:
        """Set charger."""
        if not await self.async_login():
            return False

        try:
            action = "start" if activate else "stop"
            timer = " timed" if timer else ""
            _LOGGER.debug(
                "Sending command to %s%s charger to vehicle %s",
                action,
                vin,
                timer,
            )
            await self._audi_service.async_set_battery_charger(vin, activate, timer)
            action = "started" if activate else "stopped"
            _LOGGER.debug("Successfully %s%s charger of vehicle %s", action, vin, timer)
            return True
        except RequestError as error:  # pylint: disable=broad-except
            action = "start" if activate else "stop"
            _LOGGER.error(
                "Unable to %s charger of vehicle %s: %s",
                action,
                vin,
                str(error).rstrip("\n"),
            )
            return False

    async def async_set_window_heating(self, vin: str, activate: bool) -> bool:
        """Set window heating."""
        if not await self.async_login():
            return False

        try:
            action = "start" if activate else "stop"
            _LOGGER.debug(
                "Sending command to %s window heating to vehicle %s", action, vin
            )
            await self._audi_service.async_set_window_heating(vin, activate)
            action = "started" if activate else "stopped"
            _LOGGER.debug("Successfully %s window heating of vehicle %s", action, vin)
            return True
        except RequestError as error:  # pylint: disable=broad-except
            _LOGGER.error(
                "Unable to %s window heating of vehicle %s: %s",
                action,
                vin,
                str(error).rstrip("\n"),
            )
            return False

    async def async_set_pre_heater(self, vin: str, activate: bool) -> bool:
        """Set pre heater."""
        if not await self.async_login():
            return False

        try:
            action = "start" if activate else "stop"
            _LOGGER.debug("Sending command to %s pre-heater to vehicle %s", action, vin)
            await self._audi_service.async_set_pre_heater(vin, activate)
            action = "started" if activate else "stopped"
            _LOGGER.debug("Successfully %s pre-heater of vehicle %s", action, vin)
            return True
        except RequestError as error:  # pylint: disable=broad-except
            _LOGGER.error(
                "Unable to %s pre-heater of vehicle %s: %s",
                action,
                vin,
                str(error).rstrip("\n"),
            )
            return False
