import inspect
from contextlib import contextmanager
from functools import partial, update_wrapper, wraps
from types import TracebackType
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    NewType,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
    overload,
)

import httpx

from .mocks import Mocker
from .models import (
    AllMockedAssertionError,
    CallList,
    PassThrough,
    ResolvedRoute,
    Route,
    RouteList,
    SideEffectError,
)
from .patterns import Pattern, merge_patterns, parse_url_patterns
from .types import DefaultType, ResolvedResponseTypes, RouteResultTypes, URLPatternTypes

Default = NewType("Default", object)
DEFAULT = Default(...)


class Router:
    def __init__(
        self,
        *,
        assert_all_called: bool = True,
        assert_all_mocked: bool = True,
        base_url: Optional[str] = None,
    ) -> None:
        self._assert_all_called = assert_all_called
        self._assert_all_mocked = assert_all_mocked
        self._bases = parse_url_patterns(base_url, exact=False)

        self.routes = RouteList()
        self.calls = CallList()

        self._snapshots: List[Tuple] = []
        self.snapshot()

    def clear(self) -> None:
        """
        Clears all routes. May be rolled back to snapshot state.
        """
        pass

    def snapshot(self) -> None:
        """
        Snapshots current routes and calls state.
        """
        pass

    def rollback(self) -> None:
        """
        Rollbacks routes, and optionally calls, to snapshot state.
        """
        pass

    def reset(self) -> None:
        """
        Resets call stats.
        """
        pass

    def assert_all_called(self) -> None:
        pass

    def __getitem__(self, name: str) -> Route:
        return self.routes[name]

    @overload
    def pop(self, name: str) -> Route: ...  # pragma: nocover

    @overload
    def pop(
        self, name: str, default: DefaultType
    ) -> Union[Route, DefaultType]: ...  # pragma: nocover

    def pop(self, name, default=...):
        """
        Removes a route by name and returns it.

        Raises KeyError when `default` not provided and name is not found.
        """
        pass

    def route(
        self, *patterns: Pattern, name: Optional[str] = None, **lookups: Any
    ) -> Route:
        pass

    def add(self, route: Route, *, name: Optional[str] = None) -> Route:
        """
        Adds a route with optionally given name,
        replacing any existing route with same name or pattern.
        """
        pass

    def request(
        self,
        method: str,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        pass

    def get(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        pass

    def post(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        pass

    def put(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        pass

    def patch(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        pass

    def delete(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        pass

    def head(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        pass

    def options(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        pass

    def record(
        self,
        request: httpx.Request,
        *,
        response: Optional[httpx.Response] = None,
        route: Optional[Route] = None,
    ) -> None:
        pass

    @contextmanager
    def resolver(self, request: httpx.Request) -> Generator[ResolvedRoute, None, None]:
        pass

    def resolve(self, request: httpx.Request) -> ResolvedRoute:
        pass

    async def aresolve(self, request: httpx.Request) -> ResolvedRoute:
        pass

    def handler(self, request: httpx.Request) -> httpx.Response:
        pass

    async def async_handler(self, request: httpx.Request) -> httpx.Response:
        pass


class MockRouter(Router):
    def __init__(
        self,
        *,
        assert_all_called: bool = True,
        assert_all_mocked: bool = True,
        base_url: Optional[str] = None,
        using: Optional[Union[str, Default]] = DEFAULT,
    ) -> None:
        super().__init__(
            assert_all_called=assert_all_called,
            assert_all_mocked=assert_all_mocked,
            base_url=base_url,
        )
        self.Mocker: Optional[Type[Mocker]] = None
        self._using = using

    @overload
    def __call__(
        self,
        func: None = None,
        *,
        assert_all_called: Optional[bool] = None,
        assert_all_mocked: Optional[bool] = None,
        base_url: Optional[str] = None,
        using: Optional[Union[str, Default]] = DEFAULT,
    ) -> "MockRouter": ...  # pragma: nocover

    @overload
    def __call__(
        self,
        func: Callable = ...,
        *,
        assert_all_called: Optional[bool] = None,
        assert_all_mocked: Optional[bool] = None,
        base_url: Optional[str] = None,
        using: Optional[Union[str, Default]] = DEFAULT,
    ) -> Callable: ...  # pragma: nocover

    def __call__(
        self,
        func: Optional[Callable] = None,
        *,
        assert_all_called: Optional[bool] = None,
        assert_all_mocked: Optional[bool] = None,
        base_url: Optional[str] = None,
        using: Optional[Union[str, Default]] = DEFAULT,
    ) -> Union["MockRouter", Callable]:
        """
        Decorator or Context Manager.

        Use decorator/manager with parentheses for local state, or without parentheses
        for global state, i.e. shared patterns added outside of scope.
        """
        if func is None:
            # Parentheses used, branch out to new nested instance.
            # - Only stage when using local ctx `with respx.mock(...) as respx_mock:`
            # - First stage when using local decorator `@respx.mock(...)`
            #   FYI, global ctx `with respx.mock:` hits __enter__ directly
            settings: Dict[str, Any] = {
                "base_url": base_url,
                "using": using,
            }
            if assert_all_called is not None:
                settings["assert_all_called"] = assert_all_called
            if assert_all_mocked is not None:
                settings["assert_all_mocked"] = assert_all_mocked
            respx_mock = self.__class__(**settings)
            return respx_mock

        # Determine if decorated function needs a `respx_mock` instance
        is_async = inspect.iscoroutinefunction(func)
        argspec = inspect.getfullargspec(func)
        needs_mock_reference = "respx_mock" in argspec.args

        if needs_mock_reference:
            func = partial(func, respx_mock=self)

        # Async Decorator
        async def _async_decorator(*args, **kwargs):
            pass

        # Sync Decorator
        def _sync_decorator(*args, **kwargs):
            pass

        if needs_mock_reference:
            async_decorator = wraps(func)(_async_decorator)
            sync_decorator = wraps(func)(_sync_decorator)
        else:
            async_decorator = update_wrapper(_async_decorator, func)
            sync_decorator = update_wrapper(_sync_decorator, func)

        # Dispatch async/sync decorator, depending on decorated function.
        # - Only stage when using global decorator `@respx.mock`
        # - Second stage when using local decorator `@respx.mock(...)`
        return async_decorator if is_async else sync_decorator

    def __enter__(self) -> "MockRouter":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        self.stop(quiet=bool(exc_type is not None))

    async def __aenter__(self) -> "MockRouter":
        return self.__enter__()

    async def __aexit__(self, *args: Any) -> None:
        self.__exit__(*args)

    @property
    def using(self) -> Optional[str]:
        pass

    def start(self) -> None:
        """
        Register transport, snapshot router and start patching.
        """
        pass

    def stop(self, clear: bool = True, reset: bool = True, quiet: bool = False) -> None:
        """
        Unregister transport and rollback router.
        Stop patching when no registered transports left.
        """
        pass
