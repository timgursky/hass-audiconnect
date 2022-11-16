"""Call url service."""
from __future__ import annotations

import asyncio
import base64
import hmac
import json
import logging
import os
import re
import uuid
from datetime import datetime, timedelta
from hashlib import sha256, sha512
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from bs4 import BeautifulSoup

from .auth import Auth
from .exceptions import (
    AudiException,
    InvalidFormatError,
    RequestError,
    TimeoutExceededError,
)
from .models import (
    ChargerDataResponse,
    ClimaterDataResponse,
    PositionDataResponse,
    PreheaterDataResponse,
    TripDataResponse,
    VehicleDataResponse,
)
from .util import get_attr, jload, to_byte_array, Globals

MAX_RESPONSE_ATTEMPTS = 10
REQUEST_STATUS_SLEEP = 10

SUCCEEDED = "succeeded"
FAILED = "failed"
REQUEST_SUCCESSFUL = "request_successful"
REQUEST_FAILED = "request_failed"

XCLIENT_ID = "77869e21-e30a-4a92-b016-48ab7d3db1d8"

_LOGGER = logging.getLogger(__name__)


class AudiService:
    """Audi service."""

    def __init__(
        self,
        api: Auth,
        country: str,
        spin: str,
    ) -> None:
        """Initialize."""
        self._api = api
        self._country = "DE" if country is None else country
        self._language = None
        self._type = "Audi"
        self._spin = spin
        self._home_region: dict[str, str] = {}
        self._home_region_setter: dict[str, str] = {}
        self.mbb_oauth_base_url = ""
        self.mbb_oauth_token: dict[str, Any] = {}
        self.x_client_id = ""
        self.token_endpoint = ""
        self._bearer_token_json: dict[str, str] = {}
        self._client_id = ""
        self._authorization_server_baseurl_live = ""
        self.authorization_endpoint = None
        self.revocation_endpoint = None
        self.vw_token: dict[str, str] = {}
        self.audi_token: dict[str, str] = {}

    def get_hidden_html_input_form_data(
        self, response, form_data: dict[str, str]
    ) -> dict[str, str]:
        """Parse the html body and extract the target.

        url, csrf token and other required parameters"""
        html = BeautifulSoup(response, "html.parser")
        form_inputs = html.find_all("input", attrs={"type": "hidden"})
        for form_input in form_inputs:
            name = form_input.get("name")
            form_data[name] = form_input.get("value")

        return form_data

    def get_post_url(self, response, url) -> str:
        """Parse the html body and extract the target.

        url, csrf token and other required parameters"""
        html = BeautifulSoup(response, "html.parser")
        form_tag = html.find("form")

        # Extract the target url
        action = form_tag.get("action")
        if action.startswith("http"):
            # Absolute url
            username_post_url = action
        elif action.startswith("/"):
            # Relative to domain
            url_parts = urlparse(url)
            username_post_url = url_parts.scheme + "://" + url_parts.netloc + action
        else:
            raise RequestError("Unknown form action: " + action)
        return username_post_url

    async def async_refresh_vehicle_data(self, vin: str) -> None:
        """Refresh vehicle data."""
        self._api.use_token(self.vw_token)
        home_region = await self._async_get_home_region(vin.upper())
        data = await self._api.post(
            f"{home_region}/fs-car/bs/vsr/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/requests"
        )

        request_id = get_attr(data, "CurrentVehicleDataResponse.requestId")
        vin = get_attr(data, "CurrentVehicleDataResponse.vin")

        await self.async_check_request_succeeded(
            f"{home_region}/fs-car/bs/vsr/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/requests/{request_id}/jobstatus",
            "refresh vehicle data",
            REQUEST_SUCCESSFUL,
            REQUEST_FAILED,
            "requestStatusResponse.status",
        )

    async def async_get_preheater(self, vin: str) -> PreheaterDataResponse:
        """Get preheater data."""
        self._api.use_token(self.vw_token)
        home_region = await self._async_get_home_region(vin.upper())
        data = await self._api.get(
            f"{home_region}/fs-car/bs/rs/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/status"
        )
        return PreheaterDataResponse(data)

    async def async_get_stored_vehicle_data(self, vin: str) -> VehicleDataResponse:
        """Get store data."""
        self._api.use_token(self.vw_token)
        home_region = await self._async_get_home_region(vin.upper())
        data = await self._api.get(
            f"{home_region}/fs-car/bs/vsr/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/status"
        )
        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", data)
        return VehicleDataResponse(data, self._spin)

    async def async_get_charger(self, vin: str) -> ChargerDataResponse:
        """Get charger data."""
        self._api.use_token(self.vw_token)
        home_region = await self._async_get_home_region(vin.upper())
        data = await self._api.get(
            f"{home_region}/fs-car/bs/batterycharge/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/charger"
        )
        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", data)
        return ChargerDataResponse(data)

    async def async_get_climater(self, vin: str) -> ClimaterDataResponse:
        """Get climater data."""
        self._api.use_token(self.vw_token)
        home_region = await self._async_get_home_region(vin.upper())
        data = await self._api.get(
            f"{home_region}/fs-car/bs/climatisation/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/climater"
        )
        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", data)
        return ClimaterDataResponse(data)

    async def async_get_stored_position(self, vin: str) -> PositionDataResponse:
        """Get position data."""
        self._api.use_token(self.vw_token)
        home_region = await self._async_get_home_region(vin.upper())
        data = await self._api.get(
            f"{home_region}/fs-car/bs/cf/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/position"
        )
        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", data)
        return PositionDataResponse(data)

    async def async_get_operations_list(self, vin: str) -> dict[str, str]:
        """Get operation data."""
        self._api.use_token(self.vw_token)
        data = await self._api.get(
            f"https://mal-1a.prd.ece.vwg-connect.com/api/rolesrights/operationlist/v3/vehicles/{vin.upper()}"
        )
        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", data)
        return data

    async def async_get_timer(self, vin: str) -> dict[str, str]:
        """Get timer."""
        self._api.use_token(self.vw_token)
        home_region = await self._async_get_home_region(vin.upper())
        data = await self._api.get(
            f"{home_region}/fs-car/bs/departuretimer/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/timer"
        )
        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", data)
        return data

    async def async_get_vehicles(self) -> dict[str, str]:
        """Get all vehicles."""
        self._api.use_token(self.vw_token)
        data = await self._api.get(
            f"https://msg.volkswagen.de/fs-car/usermanagement/users/v1/{self._type}/{self._country}/vehicles"
        )
        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", data)
        return data

    async def async_get_vehicle_information(self):
        """Get vehicle information."""
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "X-App-Name": "myAudi",
            "X-App-Version": Auth.HDR_XAPP_VERSION,
            "Accept-Language": f"{self._language}-{self._country.upper()}",
            "X-User-Country": self._country.upper(),
            "User-Agent": Auth.HDR_USER_AGENT,
            "Authorization": "Bearer " + self.audi_token["access_token"],
            "Content-Type": "application/json; charset=utf-8",
        }
        req_data = {
            "query": "query vehicleList {\n userVehicles {\n vin\n mappingVin\n vehicle { core { modelYear\n }\n media { shortName\n longName }\n }\n csid\n commissionNumber\n type\n devicePlatform\n mbbConnect\n userRole {\n role\n }\n vehicle {\n classification {\n driveTrain\n }\n }\n nickname\n }\n}"
        }
        rep_rsptxt = await self._api.request(
            "POST",
            "https://app-api.live-my.audi.com/vgql/v1/graphql",
            json.dumps(req_data),
            headers=headers,
            allow_redirects=False,
            rsp_txt=True,
        )
        vins = jload(rep_rsptxt)
        if "data" not in vins:
            raise InvalidFormatError("Invalid json in vehicle information")
        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", vins["data"])
        return vins["data"]

    async def async_get_vehicle_data(self, vin: str) -> dict[str, str]:
        """Get vehicle data."""
        self._api.use_token(self.vw_token)
        home_region = await self._async_get_home_region(vin.upper())
        data = await self._api.get(
            f"{home_region}/fs-car/vehicleMgmt/vehicledata/v2/{self._type}/{self._country}/vehicles/{vin.upper()}/"
        )
        _LOGGER.debug("RESPONSE: %s", data)
        return data

    async def async_get_tripdata(
        self, vin: str, kind: str
    ) -> tuple[TripDataResponse, TripDataResponse]:
        """Get trip data."""
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "X-App-Name": "myAudi",
            "X-App-Version": Auth.HDR_XAPP_VERSION,
            "X-Client-ID": self.x_client_id,
            "User-Agent": Auth.HDR_USER_AGENT,
            "Authorization": "Bearer " + self.vw_token["access_token"],
        }
        td_reqdata = {
            "type": "list",
            "from": "1970-01-01T00:00:00Z",
            # "from":(datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": (datetime.utcnow() + timedelta(minutes=90)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        }
        home_region = await self._async_get_home_region(vin.upper())

        data = await self._api.request(
            "GET",
            f"{home_region}/api/bs/tripstatistics/v1/vehicles/{vin.upper()}/tripdata/{kind}",
            None,
            params=td_reqdata,
            headers=headers,
        )
        td_sorted = sorted(
            get_attr(data, "tripDataList.tripData"),
            key=lambda k: k["overallMileage"],
            reverse=True,
        )

        td_current = td_sorted[0]
        td_reset_trip = None

        for trip in td_sorted:
            if (td_current["startMileage"] - trip["startMileage"]) > 2:
                td_reset_trip = trip
                break
            else:
                td_current["tripID"] = trip["tripID"]
                td_current["startMileage"] = trip["startMileage"]

        if Globals.debug_level(self) >= 1:
            _LOGGER.debug("RESPONSE: %s", td_current)
            _LOGGER.debug("RESPONSE: %s", td_reset_trip)

        return TripDataResponse(td_current), TripDataResponse(td_reset_trip)

    async def _async_fill_home_region(self, vin: str) -> None:
        """Fill region."""
        self._home_region[vin] = "https://msg.volkswagen.de"
        self._home_region_setter[vin] = "https://mal-1a.prd.ece.vwg-connect.com"

        try:
            self._api.use_token(self.vw_token)
            res = await self._api.get(
                f"https://mal-1a.prd.ece.vwg-connect.com/api/cs/vds/v1/vehicles/{vin}/homeRegion"
            )
            if (
                uri := get_attr(res, "homeRegion.baseUri.content")
            ) is not None and uri != "https://mal-1a.prd.ece.vwg-connect.com/api":
                self._home_region_setter[vin] = uri.split("/api")[0]
                self._home_region[vin] = self._home_region_setter[vin].replace(
                    "mal-", "fal-"
                )
        except Exception:  # pylint: disable=broad-except
            pass

    async def _async_get_home_region(self, vin: str) -> str:
        """Get region."""
        if self._home_region.get(vin) is not None:
            return self._home_region[vin]

        await self._async_fill_home_region(vin)

        return self._home_region[vin]

    async def _async_get_home_region_setter(self, vin: str) -> str:
        """Get region setter."""
        if self._home_region_setter.get(vin) is not None:
            return self._home_region_setter[vin]

        await self._async_fill_home_region(vin)

        return self._home_region_setter[vin]

    async def _async_get_security_token(self, vin: str, action: str) -> str:
        """Get security token."""
        home_region_setter = await self._async_get_home_region_setter(vin.upper())

        # Challenge
        headers = {
            "User-Agent": "okhttp/3.7.0",
            "X-App-Version": "3.14.0",
            "X-App-Name": "myAudi",
            "Accept": "application/json",
            "Authorization": "Bearer " + self.vw_token["access_token"],
        }

        body = await self._api.request(
            "GET",
            f"{home_region_setter}/api/rolesrights/authorization/v2/vehicles/{vin.upper()}/services/{action}/security-pin-auth-requested",
            headers=headers,
            data=None,
        )

        sec_token = get_attr(body, "securityPinAuthInfo.securityToken")
        challenge = get_attr(
            body, "securityPinAuthInfo.securityPinTransmission.challenge"
        )

        # Response
        security_pin_hash = self._generate_security_pin_hash(challenge)
        data = {
            "securityPinAuthentication": {
                "securityPin": {
                    "challenge": challenge,
                    "securityPinHash": security_pin_hash,
                },
                "securityToken": sec_token,
            }
        }

        headers = {
            "User-Agent": "okhttp/3.7.0",
            "Content-Type": "application/json",
            "X-App-Version": "3.14.0",
            "X-App-Name": "myAudi",
            "Accept": "application/json",
            "Authorization": "Bearer " + self.vw_token["access_token"],
        }

        body = await self._api.request(
            "POST",
            f"{home_region_setter}/api/rolesrights/authorization/v2/security-pin-auth-completed",
            headers=headers,
            data=json.dumps(data),
        )
        return body["securityToken"]

    def _async_get_vehicle_action_header(
        self, content_type: str, security_token: str | None
    ) -> dict[str, str]:
        """Get header for action."""
        headers = {
            "User-Agent": "okhttp/3.7.0",
            "Host": "msg.volkswagen.de",
            "X-App-Version": "3.14.0",
            "X-App-Name": "myAudi",
            "Authorization": "Bearer " + self.vw_token["access_token"],
            "Accept-charset": "UTF-8",
            "Content-Type": content_type,
            "Accept": "application/json, application/vnd.vwg.mbb.ChargerAction_v1_0_0+xml,application/vnd.volkswagenag.com-error-v1+xml,application/vnd.vwg.mbb.genericError_v1_0_2+xml, application/vnd.vwg.mbb.RemoteStandheizung_v2_0_0+xml, application/vnd.vwg.mbb.genericError_v1_0_2+xml,application/vnd.vwg.mbb.RemoteLockUnlock_v1_0_0+xml,*/*",
        }

        if security_token is not None:
            headers["x-mbbSecToken"] = security_token

        return headers

    async def async_set_lock(self, vin: str, lock: bool) -> None:
        """Set lock."""
        home_region = await self._async_get_home_region(vin.upper())
        security_token = await self._async_get_security_token(
            vin, "rlu_v1/operations/" + ("LOCK" if lock else "UNLOCK")
        )
        action = "lock" if lock else "unlock"
        data = f'<?xml version="1.0" encoding= "UTF-8" ?><rluAction xmlns="http://audi.de/connect/rlu"><action>{action}</action></rluAction>'
        headers = self._async_get_vehicle_action_header(
            "application/vnd.vwg.mbb.RemoteLockUnlock_v1_0_0+xml", security_token
        )

        res = await self._api.request(
            "POST",
            f"{home_region}/fs-car/bs/rlu/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/actions",
            headers=headers,
            data=data,
        )

        request_id = get_attr(res, "rluActionResponse.requestId")
        await self.async_check_request_succeeded(
            f"{home_region}/fs-car/bs/rlu/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/requests/{request_id}/status",
            "lock vehicle" if lock else "unlock vehicle",
            REQUEST_SUCCESSFUL,
            REQUEST_FAILED,
            "requestStatusResponse.status",
        )

    async def async_set_battery_charger(
        self, vin: str, start: bool, timer: bool
    ) -> None:
        """Set charger."""
        home_region = await self._async_get_home_region(vin.upper())
        if start and timer:
            data = '{ "action": { "type": "selectChargingMode", "settings": { "chargeModeSelection": { "value": "timerBasedCharging" } } }}'
        elif start:
            data = '{ "action": { "type": "start" }}'
        else:
            data = '{ "action": { "type": "stop" }}'

        headers = self._async_get_vehicle_action_header("application/json", None)
        res = await self._api.request(
            "POST",
            f"{home_region}/fs-car/bs/batterycharge/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/charger/actions",
            headers=headers,
            data=data,
        )

        actionid = get_attr(res, "action.actionId")
        await self.async_check_request_succeeded(
            f"{home_region}/fs-car/bs/batterycharge/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/charger/actions/{actionid}",
            "start charger" if start else "stop charger",
            SUCCEEDED,
            FAILED,
            "action.actionState",
        )

    async def async_set_climatisation(self, vin: str, start: bool) -> None:
        """Set Climatisation."""
        home_region = await self._async_get_home_region(vin.upper())
        if start:
            data = '{"action":{"type": "startClimatisation","settings": {"targetTemperature": 2940,"climatisationWithoutHVpower": true,"heaterSource": "electric","climaterElementSettings": {"isClimatisationAtUnlock": false, "isMirrorHeatingEnabled": true,}}}}'
        else:
            data = '{"action":{"type": "stopClimatisation"}}'

        headers = self._async_get_vehicle_action_header("application/json", None)
        res = await self._api.request(
            "POST",
            f"{home_region}/fs-car/bs/climatisation/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/climater/actions",
            headers=headers,
            data=data,
        )
        actionid = get_attr(res, "action.actionId")
        await self.async_check_request_succeeded(
            f"{home_region}/fs-car/bs/climatisation/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/climater/actions/{actionid}",
            "start climatisation" if start else "stop climatisation",
            SUCCEEDED,
            FAILED,
            "action.actionState",
        )

    async def async_set_window_heating(self, vin: str, start: bool) -> None:
        """Set window heating."""
        home_region = await self._async_get_home_region(vin.upper())
        action = "startWindowHeating" if start else "stopWindowHeating"
        data = f'<?xml version="1.0" encoding= "UTF-8" ?><action><type>{action}</type></action>'

        headers = self._async_get_vehicle_action_header(
            "application/vnd.vwg.mbb.ClimaterAction_v1_0_0+xml", None
        )
        res = await self._api.request(
            "POST",
            f"{home_region}/fs-car/bs/climatisation/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/climater/actions",
            headers=headers,
            data=data,
        )
        actionid = get_attr(res, "action.actionId")
        await self.async_check_request_succeeded(
            f"{home_region}/fs-car/bs/climatisation/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/climater/actions/{actionid}",
            "start window heating" if start else "stop window heating",
            SUCCEEDED,
            FAILED,
            "action.actionState",
        )

    async def async_set_pre_heater(self, vin: str, activate: bool) -> None:
        """Set pre heater."""
        home_region = await self._async_get_home_region(vin.upper())
        security_token = await self._async_get_security_token(
            vin, "rheating_v1/operations/P_QSACT"
        )
        action = "true" if activate else "false"
        input_xml = f'<performAction xmlns="http://audi.de/connect/rs"><quickstart><active>{action}</active></quickstart></performAction>'
        data = f'<?xml version="1.0" encoding= "UTF-8" ?>{input_xml}'

        headers = self._async_get_vehicle_action_header(
            "application/vnd.vwg.mbb.RemoteStandheizung_v2_0_0+xml", security_token
        )
        await self._api.request(
            "POST",
            f"{home_region}/fs-car/bs/rs/v1/{self._type}/{self._country}/vehicles/{vin.upper()}/action",
            headers=headers,
            data=data,
        )

    async def async_check_request_succeeded(
        self, url: str, action: str, success: str, failed: str, path: str
    ) -> None:
        """Check request succeeded."""
        stauts_good = False
        for _ in range(MAX_RESPONSE_ATTEMPTS):
            await asyncio.sleep(REQUEST_STATUS_SLEEP)

            self._api.use_token(self.vw_token)
            res = await self._api.get(url)

            status = get_attr(res, path)

            if status is None or (failed is not None and status == failed):
                raise RequestError(("Cannot %s, return code '%s'", action, status))

            if status == success:
                stauts_good = True
                break

        if stauts_good is False:
            raise TimeoutExceededError(("Cannot %s, operation timed out", action))

    # TR/2022-06-15: New secrect for X_QMAuth
    def _calculate_x_qmauth(self) -> str:
        """Calculate X-QMAuth value."""
        gmtime_100sec = int(
            (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() / 100
        )
        xqmauth_secret = bytes(
            [
                256 - 28,
                120,
                102,
                55,
                256 - 114,
                256 - 16,
                101,
                256 - 116,
                256 - 25,
                93,
                113,
                0,
                122,
                256 - 128,
                256 - 97,
                52,
                97,
                107,
                256 - 106,
                53,
                256 - 30,
                256 - 20,
                34,
                256 - 126,
                69,
                120,
                76,
                31,
                99,
                256 - 24,
                256 - 115,
                6,
            ]
        )
        xqmauth_val = hmac.new(
            xqmauth_secret,
            str(gmtime_100sec).encode("ascii", "ignore"),
            digestmod="sha256",
        ).hexdigest()

        return "v1:c95f4fd2:" + xqmauth_val

    # TR/2021-12-01: Refresh token before it expires
    # returns True when refresh was required and successful, otherwise False
    async def async_refresh_token_if_necessary(self, elapsed_sec: float) -> bool:
        """Refresh token if."""
        if self.mbb_oauth_token is None:
            return False
        if "refresh_token" not in self.mbb_oauth_token:
            return False
        if "expires_in" not in self.mbb_oauth_token:
            return False

        if (elapsed_sec + 5 * 60) < self.mbb_oauth_token["expires_in"]:
            # refresh not needed now
            return False

        try:
            headers = {
                "Accept": "application/json",
                "Accept-Charset": "utf-8",
                "User-Agent": Auth.HDR_USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Client-ID": self.x_client_id,
            }
            mbboauth_refresh_data = {
                "grant_type": "refresh_token",
                "token": self.mbb_oauth_token["refresh_token"],
                "scope": "sc2:fal",
                # "vin": vin,  << App uses a dedicated VIN here, but it works without, don't know
            }
            encoded_mbboauth_refresh_data = urlencode(
                mbboauth_refresh_data, encoding="utf-8"
            ).replace("+", "%20")
            mbboauth_refresh_rsptxt = await self._api.request(
                "POST",
                self.mbb_oauth_base_url + "/mobile/oauth2/v1/token",
                encoded_mbboauth_refresh_data,
                headers=headers,
                allow_redirects=False,
                rsp_txt=True,
            )

            # this code is the old "vwToken"
            if self.vw_token is None:
                self.vw_token = jload(mbboauth_refresh_rsptxt)

            # TR/2022-02-10: If a new refresh_token is provided, save it for further refreshes
            if "refresh_token" in self.vw_token:
                self.mbb_oauth_token["refresh_token"] = self.vw_token["refresh_token"]

            # hdr
            headers = {
                "Accept": "application/json",
                "Accept-Charset": "utf-8",
                "X-QMAuth": self._calculate_x_qmauth(),
                "User-Agent": Auth.HDR_USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
            }
            # IDK token request data
            tokenreq_data = {
                "client_id": self._client_id,
                "grant_type": "refresh_token",
                "refresh_token": self._bearer_token_json.get("refresh_token"),
                "response_type": "token id_token",
            }
            # IDK token request
            encoded_tokenreq_data = urlencode(tokenreq_data, encoding="utf-8").replace(
                "+", "%20"
            )
            bearer_token_rsptxt = await self._api.request(
                "POST",
                self.token_endpoint,
                encoded_tokenreq_data,
                headers=headers,
                allow_redirects=False,
                rsp_txt=True,
            )
            self._bearer_token_json = jload(bearer_token_rsptxt)

            # AZS token
            headers = {
                "Accept": "application/json",
                "Accept-Charset": "utf-8",
                "X-App-Version": Auth.HDR_XAPP_VERSION,
                "X-App-Name": "myAudi",
                "User-Agent": Auth.HDR_USER_AGENT,
                "Content-Type": "application/json; charset=utf-8",
            }
            asz_req_data = {
                "token": self._bearer_token_json["access_token"],
                "grant_type": "id_token",
                "stage": "live",
                "config": "myaudi",
            }
            azs_token_rsptxt = await self._api.request(
                "POST",
                self._authorization_server_baseurl_live + "/token",
                json.dumps(asz_req_data),
                headers=headers,
                allow_redirects=False,
                rsp_txt=True,
            )
            azs_token_json = jload(azs_token_rsptxt)
            self.audi_token = azs_token_json

            return True

        except AudiException as error:  # pylint: disable=broad-except
            _LOGGER.error("Refresh token failed: %s", str(error))
            return False

    # TR/2021-12-01 updated to match behaviour of Android myAudi 4.5.0
    async def async_login_request(self, user: str, password: str) -> None:
        """Request login."""
        await self._async_retrieve_url_service()

        self._api.use_token(None)
        self._api.set_xclient_id(None)

        # Generate code_challenge
        code_verifier = str(base64.urlsafe_b64encode(os.urandom(32)), "utf-8").strip(
            "="
        )
        code_challenge = str(
            base64.urlsafe_b64encode(
                sha256(code_verifier.encode("ascii", "ignore")).digest()
            ),
            "utf-8",
        ).strip("=")
        code_challenge_method = "S256"

        #
        state = str(uuid.uuid4())
        nonce = str(uuid.uuid4())

        # login page
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "X-App-Version": Auth.HDR_XAPP_VERSION,
            "X-App-Name": "myAudi",
            "User-Agent": Auth.HDR_USER_AGENT,
        }
        idk_data = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": "myaudi:///",
            "scope": "address profile badge birthdate birthplace nationalIdentifier nationality profession email vin phone nickname name picture mbb gallery openid",
            "state": state,
            "nonce": nonce,
            "prompt": "login",
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
            "ui_locales": "de-de de",
        }
        idk_rsp, idk_rsptxt = await self._api.request(
            "GET",
            self.authorization_endpoint,
            None,
            headers=headers,
            params=idk_data,
            rsp_wtxt=True,
        )

        # form_data with email
        submit_data = self.get_hidden_html_input_form_data(idk_rsptxt, {"email": user})
        submit_url = self.get_post_url(idk_rsptxt, self.authorization_endpoint)
        # send email
        email_rsptxt = await self._api.request(
            "POST",
            submit_url,
            submit_data,
            headers=headers,
            cookies=idk_rsp.cookies,
            allow_redirects=True,
            rsp_txt=True,
        )

        # form_data with password
        # 2022-01-29: new HTML response uses a js two build the html form data + button.
        # Therefore it's not possible to extract hmac and other form data.
        # --> extract hmac from embedded js snippet.
        regex_res = re.findall(
            '"hmac"\s*:\s*"[0-9a-fA-F]+"',  # noqa: W605 pylint: disable=anomalous-backslash-in-string
            email_rsptxt,
        )
        if regex_res:
            submit_url = submit_url.replace("identifier", "authenticate")
            submit_data["hmac"] = regex_res[0].split(":")[1].strip('"')
            submit_data["password"] = password
        else:
            submit_data = self.get_hidden_html_input_form_data(
                email_rsptxt, {"password": password}
            )
            submit_url = self.get_post_url(email_rsptxt, submit_url)

        # send password
        pw_rsp = await self._api.request(
            "POST",
            submit_url,
            submit_data,
            headers=headers,
            cookies=idk_rsp.cookies,
            allow_redirects=False,
            raw_reply=True,
        )

        # forward1 after pwd
        fwd1_rsp = await self._api.request(
            "GET",
            pw_rsp.headers["Location"],
            None,
            headers=headers,
            cookies=idk_rsp.cookies,
            allow_redirects=False,
            raw_reply=True,
        )

        # forward2 after pwd
        fwd2_rsp = await self._api.request(
            "GET",
            fwd1_rsp.headers["Location"],
            None,
            headers=headers,
            cookies=idk_rsp.cookies,
            allow_redirects=False,
            raw_reply=True,
        )

        # get tokens
        codeauth_rsp = await self._api.request(
            "GET",
            fwd2_rsp.headers["Location"],
            None,
            headers=headers,
            cookies=fwd2_rsp.cookies,
            allow_redirects=False,
            raw_reply=True,
        )

        authcode_parsed = urlparse(
            codeauth_rsp.headers["Location"][len("myaudi:///?") :]
        )
        authcode_strings = parse_qs(authcode_parsed.path)

        # hdr
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "X-QMAuth": self._calculate_x_qmauth(),
            "User-Agent": Auth.HDR_USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        # IDK token request data
        tokenreq_data = {
            "client_id": self._client_id,
            "grant_type": "authorization_code",
            "code": authcode_strings["code"][0],
            "redirect_uri": "myaudi:///",
            "response_type": "token id_token",
            "code_verifier": code_verifier,
        }
        # IDK token request
        encoded_tokenreq_data = urlencode(tokenreq_data, encoding="utf-8").replace(
            "+", "%20"
        )
        bearer_token_rsptxt = await self._api.request(
            "POST",
            self.token_endpoint,
            encoded_tokenreq_data,
            headers=headers,
            allow_redirects=False,
            rsp_txt=True,
        )
        self._bearer_token_json = jload(bearer_token_rsptxt)

        if Globals.debug_level(self) >= 2:
            _LOGGER.debug("BEARER Token: %s", self._bearer_token_json)

        # AZS token
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "X-App-Version": Auth.HDR_XAPP_VERSION,
            "X-App-Name": "myAudi",
            "User-Agent": Auth.HDR_USER_AGENT,
            "Content-Type": "application/json; charset=utf-8",
        }
        asz_req_data = {
            "token": self._bearer_token_json["access_token"],
            "grant_type": "id_token",
            "stage": "live",
            "config": "myaudi",
        }
        azs_token_rsptxt = await self._api.request(
            "POST",
            self._authorization_server_baseurl_live + "/token",
            json.dumps(asz_req_data),
            headers=headers,
            allow_redirects=False,
            rsp_txt=True,
        )
        azs_token_json = jload(azs_token_rsptxt)
        self.audi_token = azs_token_json

        if Globals.debug_level(self) >= 2:
            _LOGGER.debug("AZS Token: %s", self.audi_token)

        # mbboauth client register
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "User-Agent": Auth.HDR_USER_AGENT,
            "Content-Type": "application/json; charset=utf-8",
        }
        mbboauth_reg_data = {
            "client_name": "SM-A405FN",
            "platform": "google",
            "client_brand": "Audi",
            "appName": "myAudi",
            "appVersion": Auth.HDR_XAPP_VERSION,
            "appId": "de.myaudi.mobile.assistant",
        }
        mbboauth_client_reg_rsp, mbboauth_client_reg_rsptxt = await self._api.request(
            "POST",
            self.mbb_oauth_base_url + "/mobile/register/v1",
            json.dumps(mbboauth_reg_data),
            headers=headers,
            allow_redirects=False,
            rsp_wtxt=True,
        )
        mbboauth_client_reg_json = jload(mbboauth_client_reg_rsptxt)
        self.x_client_id = mbboauth_client_reg_json["client_id"]
        self._api.set_xclient_id(self.x_client_id)

        # mbboauth auth
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "User-Agent": Auth.HDR_USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Client-ID": self.x_client_id,
        }
        mbboauth_auth_data = {
            "grant_type": "id_token",
            "token": self._bearer_token_json["id_token"],
            "scope": "sc2:fal",
        }
        encoded_mbboauth_auth_data = urlencode(
            mbboauth_auth_data, encoding="utf-8"
        ).replace("+", "%20")
        mbboauth_auth_rsptxt = await self._api.request(
            "POST",
            self.mbb_oauth_base_url + "/mobile/oauth2/v1/token",
            encoded_mbboauth_auth_data,
            headers=headers,
            allow_redirects=False,
            rsp_txt=True,
        )
        mbboauth_auth_json = jload(mbboauth_auth_rsptxt)
        # store token and expiration time
        self.mbb_oauth_token = mbboauth_auth_json

        # mbboauth refresh (app immediately refreshes the token)
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "User-Agent": Auth.HDR_USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Client-ID": self.x_client_id,
        }
        mbboauth_refresh_data = {
            "grant_type": "refresh_token",
            "token": mbboauth_auth_json["refresh_token"],
            "scope": "sc2:fal",
            # "vin": vin,  << App uses a dedicated VIN here, but it works without, don't know
        }
        encoded_mbboauth_refresh_data = urlencode(
            mbboauth_refresh_data, encoding="utf-8"
        ).replace("+", "%20")
        mbboauth_refresh_rsptxt = await self._api.request(
            "POST",
            self.mbb_oauth_base_url + "/mobile/oauth2/v1/token",
            encoded_mbboauth_refresh_data,
            headers=headers,
            allow_redirects=False,
            cookies=mbboauth_client_reg_rsp.cookies,
            rsp_txt=True,
        )
        # this code is the old "vwToken"
        self.vw_token = jload(mbboauth_refresh_rsptxt)

        if Globals.debug_level(self) >= 2:
            _LOGGER.debug("MBB Token: %s", self.vw_token)

    def _generate_security_pin_hash(self, challenge) -> str:
        """Generate security pin hash."""
        pin = to_byte_array(self._spin)
        byte_challenge = to_byte_array(challenge)
        b_pin = bytes(pin + byte_challenge)
        return sha512(b_pin).hexdigest().upper()

    async def _async_retrieve_url_service(self):
        """Get urls for request."""
        # Get markets to get language
        markets_json = await self._api.request(
            "GET",
            "https://content.app.my.audi.com/service/mobileapp/configurations/markets",
            None,
        )

        country_spec = get_attr(markets_json, "countries.countrySpecifications")
        if self._country.upper() not in country_spec:
            raise AudiException("Country not found")

        self._language = country_spec.get(self._country.upper(), {}).get(
            "defaultLanguage"
        )

        # Dynamic configuration URLs
        marketcfg_url = f"https://content.app.my.audi.com/service/mobileapp/configurations/market/{self._country}/{self._language}?v=4.6.0"

        # Get market config to get client_id , Authorization base url and mbbOAuth base url
        marketcfg_json = await self._api.request("GET", marketcfg_url, None)

        # use dynamic config from marketcfg
        self._client_id = "09b6cbec-cd19-4589-82fd-363dfa8c24da@apps_vw-dilab_com"
        if "idkClientIDAndroidLive" in marketcfg_json:
            self._client_id = marketcfg_json["idkClientIDAndroidLive"]
        _LOGGER.debug("Client id: %s", self._client_id)

        self._authorization_server_baseurl_live = (
            "https://aazsproxy-service.apps.emea.vwapps.io"
        )
        if "authorizationServerBaseURLLive" in marketcfg_json:
            self._authorization_server_baseurl_live = marketcfg_json[
                "authorizationServerBaseURLLive"
            ]
        self.mbb_oauth_base_url = (
            "https://mbboauth-1d.prd.ece.vwg-connect.com/mbbcoauth"
        )
        if "mbbOAuthBaseURLLive" in marketcfg_json:
            self.mbb_oauth_base_url = marketcfg_json["mbbOAuthBaseURLLive"]

        _LOGGER.debug("AAZEndpoint: %s", self._authorization_server_baseurl_live)
        _LOGGER.debug("MBBOAuth: %s", self.mbb_oauth_base_url)

        # use dynamic config from openId config
        # Get openId config to get authorizationEndpoint, tokenEndpoint, RevocationEndpoint
        zone = "na" if self._country.upper() == "US" else "emea"
        openidcfg_url = f"https://idkproxy-service.apps.{zone}.vwapps.io/v1/{zone}/openid-configuration"
        openidcfg_json = await self._api.request("GET", openidcfg_url, None)

        # authorization endpoint
        self.authorization_endpoint = "https://identity.vwgroup.io/oidc/v1/authorize"
        if "authorization_endpoint" in openidcfg_json:
            self.authorization_endpoint = openidcfg_json["authorization_endpoint"]

        # token endpoint
        self.token_endpoint = (
            "https://idkproxy-service.apps.emea.vwapps.io/v1/emea/token"
        )
        if "token_endpoint" in openidcfg_json:
            self.token_endpoint = openidcfg_json["token_endpoint"]

        # revocation endpoint
        revocation_endpoint = (
            "https://idkproxy-service.apps.emea.vwapps.io/v1/emea/revoke"
        )
        if revocation_endpoint in openidcfg_json:
            self.revocation_endpoint = openidcfg_json["revocation_endpoint"]

        _LOGGER.debug("AuthEndpoint: %s", self.authorization_endpoint)
        _LOGGER.debug("TokenEndpoint: %s", self.token_endpoint)
        _LOGGER.debug("RevocationEndpoint: %s", self.revocation_endpoint)
