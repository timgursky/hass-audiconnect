"""Audi connect."""
from __future__ import annotations

import json
import logging
from asyncio import CancelledError, TimeoutError  # pylint: disable=redefined-builtin
from datetime import datetime

import async_timeout
from aiohttp.hdrs import METH_GET, METH_POST, METH_PUT
from .exceptions import TimeoutExceededError, HttpRequestError, RequestError
from .util import Globals

TIMEOUT = 120

_LOGGER = logging.getLogger(__name__)


class Auth:
    """Authentication."""

    HDR_XAPP_VERSION = "4.9.2"
    HDR_USER_AGENT = "myAudi-Android/4.9.2 (Build 800237696.2205091738) Android/11"

    def __init__(self, session, proxy=None) -> None:
        """Initialize."""
        self.__token = None
        self.__xclientid = None
        self._session = session
        if proxy is not None:
            self.__proxy: dict[  # pylint: disable=unused-private-member
                str, str
            ] | None = {
                "http": proxy,
                "https": proxy,
            }
        else:
            self.__proxy = None  # pylint: disable=unused-private-member

    def use_token(self, token):
        """Use token."""
        self.__token = token

    def set_xclient_id(self, xclientid):
        """Set x client id."""
        self.__xclientid = xclientid

    async def request(
        self,
        method,
        url,
        data,
        headers: dict[str, str] = None,
        raw_reply: bool = False,
        raw_contents: bool = False,
        rsp_wtxt: bool = False,
        rsp_txt: bool = False,
        **kwargs,
    ):
        """Request url with method."""
        try:
            with async_timeout.timeout(TIMEOUT):
                if Globals.debug_level(self) >= 2:
                    _LOGGER.debug("HEADER: %s", headers)
                    if method == "POST":
                        _LOGGER.debug("POST DATA:%s", data)
                _LOGGER.debug("METHOD:%s URL:%s", method, url)
                async with self._session.request(
                    method, url, headers=headers, data=data, **kwargs
                ) as response:
                    _LOGGER.debug("RESPONSE: %s", response.status)
                    if raw_reply:
                        return response
                    elif rsp_txt:
                        return await response.text()
                    elif rsp_wtxt:
                        txt = await response.text()
                        return response, txt
                    elif raw_contents:
                        return await response.read()
                    elif response.status == 200 or response.status == 202:
                        return await response.json(loads=json_loads)
                    else:
                        raise RequestError(
                            response.request_info,
                            response.history,
                            status=response.status,
                            message=response.reason,
                        )
        except (CancelledError, TimeoutError) as error:
            raise TimeoutExceededError("Timeout error") from error
        except RequestError as error:
            raise error
        except Exception as error:
            raise HttpRequestError(error) from error

    async def get(
        self, url, raw_reply: bool = False, raw_contents: bool = False, **kwargs
    ):
        """GET request."""
        full_headers = self.__get_headers()
        response = await self.request(
            METH_GET,
            url,
            data=None,
            headers=full_headers,
            raw_reply=raw_reply,
            raw_contents=raw_contents,
            **kwargs,
        )
        return response

    async def put(self, url, data=None, headers: dict[str, str] = None):
        """PUT request."""
        full_headers = self.__get_headers()
        if headers is not None:
            full_headers.update(headers)
        response = await self.request(METH_PUT, url, headers=full_headers, data=data)
        return response

    async def post(
        self,
        url,
        data=None,
        headers: dict[str, str] = None,
        use_json: bool = True,
        raw_reply: bool = False,
        raw_contents: bool = False,
        **kwargs,
    ):
        """POST request."""
        full_headers = self.__get_headers()
        if headers is not None:
            full_headers.update(headers)
        if use_json and data is not None:
            data = json.dumps(data)
        response = await self.request(
            METH_POST,
            url,
            headers=full_headers,
            data=data,
            raw_reply=raw_reply,
            raw_contents=raw_contents,
            **kwargs,
        )
        return response

    def __get_headers(self):
        """Prepare header."""
        data = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "X-App-Version": self.HDR_XAPP_VERSION,
            "X-App-Name": "myAudi",
            "User-Agent": self.HDR_USER_AGENT,
        }
        if self.__token is not None:
            data["Authorization"] = "Bearer " + self.__token.get("access_token")
        if self.__xclientid is not None:
            data["X-Client-ID"] = self.__xclientid

        return data


def obj_parser(obj):
    """Parse datetime."""
    for key, val in obj.items():
        try:
            obj[key] = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S%z")
        except (TypeError, ValueError):
            pass
    return obj


def json_loads(jsload):
    """Json load."""
    return json.loads(jsload, object_hook=obj_parser)
