from typing import Any, Optional, Union, overload

from .models import CallList, Route
from .patterns import Pattern
from .router import MockRouter
from .types import DefaultType, URLPatternTypes

mock = MockRouter(assert_all_called=False)

routes = mock.routes
calls: CallList = mock.calls


def start() -> None:
    pass


def stop(clear: bool = True, reset: bool = True) -> None:
    pass


def clear() -> None:
    pass


def reset() -> None:
    pass


@overload
def pop(name: str) -> Route:
    ...  # pragma: nocover


@overload
def pop(name: str, default: DefaultType) -> Union[Route, DefaultType]:
    ...  # pragma: nocover


def pop(name, default=...):
    pass


def route(*patterns: Pattern, name: Optional[str] = None, **lookups: Any) -> Route:
    pass


def add(route: Route, *, name: Optional[str] = None) -> Route:
    pass


def request(
    method: str,
    url: Optional[URLPatternTypes] = None,
    *,
    name: Optional[str] = None,
    **lookups: Any,
) -> Route:
    pass


def get(
    url: Optional[URLPatternTypes] = None, *, name: Optional[str] = None, **lookups: Any
) -> Route:
    pass


def post(
    url: Optional[URLPatternTypes] = None, *, name: Optional[str] = None, **lookups: Any
) -> Route:
    pass


def put(
    url: Optional[URLPatternTypes] = None, *, name: Optional[str] = None, **lookups: Any
) -> Route:
    pass


def patch(
    url: Optional[URLPatternTypes] = None, *, name: Optional[str] = None, **lookups: Any
) -> Route:
    pass


def delete(
    url: Optional[URLPatternTypes] = None, *, name: Optional[str] = None, **lookups: Any
) -> Route:
    pass


def head(
    url: Optional[URLPatternTypes] = None, *, name: Optional[str] = None, **lookups: Any
) -> Route:
    pass


def options(
    url: Optional[URLPatternTypes] = None, *, name: Optional[str] = None, **lookups: Any
) -> Route:
    pass
