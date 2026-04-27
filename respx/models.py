import inspect
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)
from unittest import mock
from warnings import warn

import httpx

from respx.utils import SetCookie

from .patterns import M, Pattern
from .types import (
    CallableSideEffect,
    Content,
    CookieTypes,
    HeaderTypes,
    ResolvedResponseTypes,
    RouteResultTypes,
    SideEffectListTypes,
    SideEffectTypes,
)


def clone_response(response: httpx.Response, request: httpx.Request) -> httpx.Response:
    """
    Clones a httpx Response for given request.
    """
    pass


class Call(NamedTuple):
    request: httpx.Request
    optional_response: Optional[httpx.Response]

    @property
    def response(self) -> httpx.Response:
        pass

    @property
    def has_response(self) -> bool:
        pass


class CallList(list, mock.NonCallableMock):
    def __init__(self, *args: Sequence[Call], name: Any = "respx") -> None:
        pass

    @property
    def called(self) -> bool:  # type: ignore[override]
        pass

    @property
    def call_count(self) -> int:  # type: ignore[override]
        pass

    @property
    def last(self) -> Call:
        pass

    def record(
        self, request: httpx.Request, response: Optional[httpx.Response]
    ) -> Call:
        pass


class MockResponse(httpx.Response):
    def __init__(
        self,
        status_code: Optional[int] = None,
        *,
        content: Optional[Content] = None,
        content_type: Optional[str] = None,
        http_version: Optional[str] = None,
        cookies: Optional[Union[CookieTypes, Sequence[SetCookie]]] = None,
        **kwargs: Any,
    ) -> None:
        pass


class Route:
    def __init__(
        self,
        *patterns: Pattern,
        **lookups: Any,
    ) -> None:
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Route):
            return False  # pragma: nocover
        return self.pattern == other.pattern

    def __repr__(self):  # pragma: nocover
        name = f"name={self._name!r} " if self._name else ""
        return f"<Route {name}{self.pattern!r}>"

    def __call__(self, side_effect: CallableSideEffect) -> CallableSideEffect:
        self.side_effect = side_effect
        return side_effect

    def __mod__(self, response: Union[int, Dict[str, Any], httpx.Response]) -> "Route":
        if isinstance(response, int):
            self.return_value = httpx.Response(status_code=response)

        elif isinstance(response, dict):
            response.setdefault("status_code", 200)
            self.return_value = httpx.Response(**response)

        elif isinstance(response, httpx.Response):
            self.return_value = response

        else:
            raise TypeError(
                f"Route can only % with int, dict or Response, got {response!r}"
            )

        return self

    @property
    def name(self) -> Optional[str]:
        pass

    @name.setter
    def name(self, name: str) -> None:
        raise NotImplementedError("Can't set name on route.")

    @property
    def pattern(self) -> Pattern:
        pass

    @pattern.setter
    def pattern(self, pattern: Pattern) -> None:
        raise NotImplementedError("Can't change route pattern.")

    @property
    def return_value(self) -> Optional[httpx.Response]:
        pass

    @return_value.setter
    def return_value(self, return_value: Optional[httpx.Response]) -> None:
        pass

    @property
    def side_effect(
        self,
    ) -> Optional[Union[SideEffectTypes, Sequence[SideEffectListTypes]]]:
        pass

    @side_effect.setter
    def side_effect(
        self,
        side_effect: Optional[Union[SideEffectTypes, Sequence[SideEffectListTypes]]],
    ) -> None:
        pass

    def snapshot(self) -> None:
        # Clone iterator-type side effect to not get pre-exhausted when rolled back
        pass

    def rollback(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def mock(
        self,
        return_value: Optional[httpx.Response] = None,
        *,
        side_effect: Optional[
            Union[SideEffectTypes, Sequence[SideEffectListTypes]]
        ] = None,
    ) -> "Route":
        pass

    def respond(
        self,
        status_code: int = 200,
        *,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[Union[CookieTypes, Sequence[SetCookie]]] = None,
        content: Optional[Content] = None,
        text: Optional[str] = None,
        html: Optional[str] = None,
        json: Any = None,
        stream: Optional[Union[httpx.SyncByteStream, httpx.AsyncByteStream]] = None,
        content_type: Optional[str] = None,
        http_version: Optional[str] = None,
        **kwargs: Any,
    ) -> "Route":
        pass

    def pass_through(self, value: bool = True) -> "Route":
        pass

    @property
    def is_pass_through(self) -> bool:
        pass

    @property
    def called(self) -> bool:
        pass

    @property
    def call_count(self) -> int:
        pass

    def _next_side_effect(
        self,
    ) -> Union[CallableSideEffect, Exception, Type[Exception], httpx.Response]:
        pass

    def _call_side_effect(
        self, effect: CallableSideEffect, request: httpx.Request, **kwargs: Any
    ) -> RouteResultTypes:
        # Add route kwarg if the side effect wants it
        pass

    def _resolve_side_effect(
        self, request: httpx.Request, **kwargs: Any
    ) -> RouteResultTypes:
        pass

    def resolve(self, request: httpx.Request, **kwargs: Any) -> RouteResultTypes:
        pass

    def match(self, request: httpx.Request) -> RouteResultTypes:
        """
        Matches and resolves request with given patterns and optional side effect.

        Returns None for a non-matching route, mocked response for a match,
        or input request for pass-through.
        """
        pass


class RouteList:
    _routes: List[Route]
    _names: Dict[str, Route]

    def __init__(self, routes: Optional["RouteList"] = None) -> None:
        pass

    def __repr__(self) -> str:
        return repr(self._routes)  # pragma: nocover

    def __iter__(self) -> Iterator[Route]:
        return iter(self._routes)

    def __bool__(self) -> bool:
        return bool(self._routes)

    def __len__(self) -> int:
        return len(self._routes)

    def __contains__(self, name: str) -> bool:
        return name in self._names

    def __getitem__(self, key: Union[int, str]) -> Route:
        if isinstance(key, int):
            return self._routes[key]
        else:
            return self._names[key]

    def __setitem__(self, i: slice, routes: "RouteList") -> None:
        """
        Re-set all routes to given routes.
        """
        if (i.start, i.stop, i.step) != (None, None, None):
            raise TypeError("Can't slice assign routes")
        self._routes = list(routes._routes)
        self._names = dict(routes._names)

    def clear(self) -> None:
        pass

    def add(self, route: Route, name: Optional[str] = None) -> Route:
        # Find route with same name
        pass

    def pop(self, name, default=...):
        """
        Removes a route by name and returns it.

        Raises KeyError when `default` not provided and name is not found.
        """
        pass


class AllMockedAssertionError(AssertionError):
    pass


class SideEffectError(Exception):
    def __init__(self, route: Route, origin: Exception) -> None:
        self.route = route
        self.origin = origin


class PassThrough(Exception):
    def __init__(self, message: str, *, request: httpx.Request, origin: Route) -> None:
        pass


class ResolvedRoute:
    def __init__(self):
        self.route: Optional[Route] = None
        self.response: Optional[ResolvedResponseTypes] = None
