import inspect
from abc import ABC
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, Dict, List, Type
from unittest import mock

import httpcore
import httpx

from respx.patterns import parse_url

from .models import AllMockedAssertionError, PassThrough
from .transports import TryTransport

if TYPE_CHECKING:
    from .router import Router  # pragma: nocover

__all__ = ["Mocker", "HTTPCoreMocker"]


class Mocker(ABC):
    _patches: ClassVar[List[mock._patch]]
    name: ClassVar[str]
    routers: ClassVar[List["Router"]]
    targets: ClassVar[List[str]]
    target_methods: ClassVar[List[str]]

    # Automatically register all the subclasses in this dict
    __registry: ClassVar[Dict[str, Type["Mocker"]]] = {}
    registry = MappingProxyType(__registry)

    def __init_subclass__(cls) -> None:
        if not getattr(cls, "name", None) or ABC in cls.__bases__:
            return

        if cls.name in cls.__registry:
            raise TypeError(
                "Subclasses of Mocker must define a unique name. "
                f"{cls.name!r} is already defined as {cls.__registry[cls.name]!r}"
            )

        cls.routers = []
        cls._patches = []
        cls.__registry[cls.name] = cls

    @classmethod
    def register(cls, router: "Router") -> None:
        pass

    @classmethod
    def unregister(cls, router: "Router") -> bool:
        pass

    @classmethod
    def add_targets(cls, *targets: str) -> None:
        pass

    @classmethod
    def remove_targets(cls, *targets: str) -> None:
        pass

    @classmethod
    def start(cls) -> None:
        # Ensure we only patch once!
        pass

    @classmethod
    def stop(cls, force: bool = False) -> None:
        # Ensure we don't stop patching when registered transports exists
        pass

    @classmethod
    def restart(cls) -> None:
        # Only stop and start if started
        pass

    @classmethod
    def handler(cls, httpx_request):
        pass

    @classmethod
    async def async_handler(cls, httpx_request):
        pass

    @classmethod
    def mock(cls, spec):
        pass


class HTTPXMocker(Mocker):
    name = "httpx"
    targets = [
        "httpx._client.Client",
        "httpx._client.AsyncClient",
    ]
    target_methods = ["_transport_for_url"]

    @classmethod
    def mock(cls, spec):
        def _transport_for_url(self):
            pass
        pass


class AbstractRequestMocker(Mocker):
    @classmethod
    def mock(cls, spec):
        def mock(self):
            pass
        async def amock(self):
            pass
        pass
    def _send_sync_request(cls, httpx_request, *, target_spec, instance, **kwargs):
        pass

    @classmethod
    async def _send_async_request(
        cls, httpx_request, *, target_spec, instance, **kwargs
    ):
        pass

    @classmethod
    def prepare_sync_request(cls, httpx_request, **kwargs):
        """
        Sync pre-read request body
        """
        pass

    @classmethod
    async def prepare_async_request(cls, httpx_request, **kwargs):
        """
        Async pre-read request body
        """
        pass

    @classmethod
    def to_httpx_request(cls, **kwargs):
        pass

    @classmethod
    def from_sync_httpx_response(cls, httpx_response, target, **kwargs):
        pass

    @classmethod
    async def from_async_httpx_response(cls, httpx_response, target, **kwargs):
        pass


class HTTPCoreMocker(AbstractRequestMocker):
    name = "httpcore"
    targets = [
        "httpcore._sync.connection.HTTPConnection",
        "httpcore._sync.connection_pool.ConnectionPool",
        "httpcore._sync.http_proxy.HTTPProxy",
        "httpcore._async.connection.AsyncHTTPConnection",
        "httpcore._async.connection_pool.AsyncConnectionPool",
        "httpcore._async.http_proxy.AsyncHTTPProxy",
    ]
    target_methods = ["handle_request", "handle_async_request"]

    @classmethod
    def prepare_sync_request(cls, httpx_request, **kwargs):
        """
        Sync pre-read request body, and update transport request arg.
        """
        pass

    @classmethod
    async def prepare_async_request(cls, httpx_request, **kwargs):
        """
        Async pre-read request body, and update transport request arg.
        """
        pass

    @classmethod
    def to_httpx_request(cls, **kwargs):
        """
        Create a `HTTPX` request from transport request arg.
        """
        pass

    @classmethod
    def from_sync_httpx_response(cls, httpx_response, target, **kwargs):
        """
        Create a `httpcore` response from a `HTTPX` response.
        """
        pass

    @classmethod
    async def from_async_httpx_response(cls, httpx_response, target, **kwargs):
        """
        Create a `httpcore` response from a `HTTPX` response.
        """
        pass


DEFAULT_MOCKER: str = HTTPCoreMocker.name
