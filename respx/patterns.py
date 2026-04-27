import io
import json as jsonlib
import operator
import pathlib
import re
from abc import ABC
from enum import Enum
from functools import reduce
from http.cookies import SimpleCookie
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Mapping,
    Optional,
    Pattern as RegexPattern,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)
from unittest.mock import ANY

import httpx

from respx.utils import MultiItems, decode_data

from .types import (
    URL as RawURL,
    CookieTypes,
    FileTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestFiles,
    URLPatternTypes,
)


class Lookup(Enum):
    EQUAL = "eq"
    REGEX = "regex"
    STARTS_WITH = "startswith"
    CONTAINS = "contains"
    IN = "in"


class Match:
    def __init__(self, matches: bool, **context: Any) -> None:
        self.matches = matches
        self.context = context

    def __bool__(self):
        return bool(self.matches)

    def __invert__(self):
        self.matches = not self.matches
        return self

    def __repr__(self):  # pragma: nocover
        return f"<Match {self.matches}>"


class Pattern(ABC):
    key: ClassVar[str]
    lookups: ClassVar[Tuple[Lookup, ...]] = (Lookup.EQUAL,)

    lookup: Lookup
    base: Optional["Pattern"]
    value: Any

    # Automatically register all the subclasses in this dict
    __registry: ClassVar[Dict[str, Type["Pattern"]]] = {}
    registry = MappingProxyType(__registry)

    def __init_subclass__(cls) -> None:
        if not getattr(cls, "key", None) or ABC in cls.__bases__:
            return

        if cls.key in cls.__registry:
            raise TypeError(
                "Subclasses of Pattern must define a unique key. "
                f"{cls.key!r} is already defined in {cls.__registry[cls.key]!r}"
            )

        cls.__registry[cls.key] = cls

    def __init__(self, value: Any, lookup: Optional[Lookup] = None) -> None:
        pass

    def __iter__(self):
        yield self

    def __bool__(self):
        return True

    def __and__(self, other: "Pattern") -> "Pattern":
        if not bool(other):
            return self
        elif not bool(self):
            return other
        return _And((self, other))

    def __or__(self, other: "Pattern") -> "Pattern":
        if not bool(other):
            return self
        elif not bool(self):
            return other
        return _Or((self, other))

    def __invert__(self):
        if not bool(self):
            return self
        return _Invert(self)

    def __repr__(self):  # pragma: nocover
        return f"<{self.__class__.__name__} {self.lookup.value} {repr(self.value)}>"

    def __hash__(self):
        return hash((self.__class__, self.lookup, self.value))

    def __eq__(self, other: object) -> bool:
        return hash(self) == hash(other)

    def clean(self, value: Any) -> Any:
        """
        Clean and return pattern value.
        """
        pass

    def parse(self, request: httpx.Request) -> Any:  # pragma: nocover
        """
        Parse and return request value to match with pattern value.
        """
        pass

    def strip_base(self, value: Any) -> Any:  # pragma: nocover
        pass

    def match(self, request: httpx.Request) -> Match:
        pass

    def _match(self, value: Any) -> Match:
        pass

    def _eq(self, value: Any) -> Match:
        pass

    def _regex(self, value: str) -> Match:
        pass

    def _startswith(self, value: str) -> Match:
        pass

    def _contains(self, value: Any) -> Match:  # pragma: nocover
        pass

    def _in(self, value: Any) -> Match:
        pass


class Noop(Pattern):
    def __init__(self) -> None:
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __bool__(self) -> bool:
        # Treat this pattern as non-existent, e.g. when filtering or conditioning
        return False

    def match(self, request: httpx.Request) -> Match:
        # If this pattern is part of a combined pattern, always be truthy, i.e. noop
        pass


class PathPattern(Pattern):
    path: Optional[str]

    def __init__(
        self, value: Any, lookup: Optional[Lookup] = None, *, path: Optional[str] = None
    ) -> None:
        pass


class _And(Pattern):
    value: Tuple[Pattern, Pattern]

    def __repr__(self):  # pragma: nocover
        a, b = self.value
        return f"{repr(a)} AND {repr(b)}"

    def __iter__(self):
        a, b = self.value
        yield from a
        yield from b

    def match(self, request: httpx.Request) -> Match:
        pass


class _Or(Pattern):
    value: Tuple[Pattern, Pattern]

    def __repr__(self):  # pragma: nocover
        a, b = self.value
        return f"{repr(a)} OR {repr(b)}"

    def __iter__(self):
        a, b = self.value
        yield from a
        yield from b

    def match(self, request: httpx.Request) -> Match:
        pass


class _Invert(Pattern):
    value: Pattern

    def __repr__(self):  # pragma: nocover
        return f"NOT {repr(self.value)}"

    def __iter__(self):
        yield from self.value

    def match(self, request: httpx.Request) -> Match:
        pass


class Method(Pattern):
    key = "method"
    lookups = (Lookup.EQUAL, Lookup.IN)
    value: Union[str, Sequence[str]]

    def clean(self, value: Union[str, Sequence[str]]) -> Union[str, Sequence[str]]:
        pass

    def parse(self, request: httpx.Request) -> str:
        pass


class MultiItemsMixin:
    lookup: Lookup
    value: Any

    def _multi_items(
        self, value: Any, *, parse_any: bool = False, encode_any: bool = False
    ) -> Tuple[Tuple[str, Tuple[Any, ...]], ...]:
        pass

    def _item_value(
        self, value: Any, parse_any: bool = False, encode_any: bool = False
    ) -> Any:
        pass

    def __hash__(self):
        return hash(
            (
                self.__class__,
                self.lookup,
                self._multi_items(self.value, encode_any=True),
            )
        )

    def _eq(self, value: Any) -> Match:
        pass

    def _contains(self, value: Any) -> Match:
        pass


class Headers(MultiItemsMixin, Pattern):
    key = "headers"
    lookups = (Lookup.CONTAINS, Lookup.EQUAL)
    value: httpx.Headers

    def clean(self, value: HeaderTypes) -> httpx.Headers:
        pass

    def parse(self, request: httpx.Request) -> httpx.Headers:
        pass


class Cookies(Pattern):
    key = "cookies"
    lookups = (Lookup.CONTAINS, Lookup.EQUAL)
    value: Set[Tuple[str, str]]

    def __hash__(self):
        return hash((self.__class__, self.lookup, tuple(sorted(self.value))))

    def clean(self, value: CookieTypes) -> Set[Tuple[str, str]]:
        pass

    def parse(self, request: httpx.Request) -> Set[Tuple[str, str]]:
        pass

    def _contains(self, value: Set[Tuple[str, str]]) -> Match:
        pass


class Scheme(Pattern):
    key = "scheme"
    lookups = (Lookup.EQUAL, Lookup.IN)
    value: Union[str, Sequence[str]]

    def clean(self, value: Union[str, Sequence[str]]) -> Union[str, Sequence[str]]:
        pass

    def parse(self, request: httpx.Request) -> str:
        pass


class Host(Pattern):
    key = "host"
    lookups = (Lookup.EQUAL, Lookup.REGEX, Lookup.IN)
    value: Union[str, RegexPattern[str], Sequence[str]]

    def clean(
        self, value: Union[str, RegexPattern[str]]
    ) -> Union[str, RegexPattern[str]]:
        pass

    def parse(self, request: httpx.Request) -> str:
        pass


class Port(Pattern):
    key = "port"
    lookups = (Lookup.EQUAL, Lookup.IN)
    value: Optional[int]

    def parse(self, request: httpx.Request) -> Optional[int]:
        pass


class Path(Pattern):
    key = "path"
    lookups = (Lookup.EQUAL, Lookup.REGEX, Lookup.STARTS_WITH, Lookup.IN)
    value: Union[str, Sequence[str], RegexPattern[str]]

    def clean(
        self, value: Union[str, RegexPattern[str]]
    ) -> Union[str, RegexPattern[str]]:
        pass

    def parse(self, request: httpx.Request) -> str:
        pass

    def strip_base(self, value: str) -> str:
        pass


class Params(MultiItemsMixin, Pattern):
    key = "params"
    lookups = (Lookup.CONTAINS, Lookup.EQUAL)
    value: httpx.QueryParams

    def clean(self, value: QueryParamTypes) -> httpx.QueryParams:
        pass

    def parse(self, request: httpx.Request) -> httpx.QueryParams:
        pass


class URL(Pattern):
    key = "url"
    lookups = (
        Lookup.EQUAL,
        Lookup.REGEX,
        Lookup.STARTS_WITH,
    )
    value: Union[str, RegexPattern[str]]

    def clean(self, value: URLPatternTypes) -> Union[str, RegexPattern[str]]:
        pass

    def parse(self, request: httpx.Request) -> str:
        pass

    def _ensure_path(self, url: httpx.URL) -> httpx.URL:
        pass


class ContentMixin:
    def parse(self, request: httpx.Request) -> Any:
        pass


class Content(ContentMixin, Pattern):
    lookups = (Lookup.EQUAL, Lookup.CONTAINS)
    key = "content"
    value: bytes

    def clean(self, value: Union[bytes, str]) -> bytes:
        pass

    def _contains(self, value: Union[bytes, str]) -> Match:
        pass


class JSON(ContentMixin, PathPattern):
    lookups = (Lookup.EQUAL,)
    key = "json"
    value: str

    def clean(self, value: Union[str, List, Dict]) -> str:
        pass

    def parse(self, request: httpx.Request) -> str:
        pass

    def hash(self, value: Union[str, List, Dict]) -> str:
        pass


class Data(MultiItemsMixin, Pattern):
    lookups = (Lookup.EQUAL, Lookup.CONTAINS)
    key = "data"
    value: MultiItems

    def _normalize_value(self, value: Any) -> Union[str, List[str]]:
        pass

    def clean(self, value: Dict[str, Any]) -> MultiItems:
        pass

    def parse(self, request: httpx.Request) -> Any:
        pass


class Files(MultiItemsMixin, Pattern):
    lookups = (Lookup.CONTAINS, Lookup.EQUAL)
    key = "files"
    value: MultiItems

    def _normalize_file_value(self, value: FileTypes) -> Tuple[Tuple[Any, Any]]:
        # Mimic httpx `FileField` to normalize `files` kwarg to shortest tuple style
        pass

    def _item_value(
        self, value: Tuple[Any, Any], parse_any: bool = False, encode_any: bool = False
    ) -> Tuple[Any, Any]:
        pass

    def clean(self, value: RequestFiles) -> MultiItems:
        pass

    def parse(self, request: httpx.Request) -> Any:
        pass


def M(*patterns: Pattern, **lookups: Any) -> Pattern:
    pass


def get_scheme_port(scheme: Optional[str]) -> Optional[int]:
    pass


def combine(patterns: Sequence[Pattern], op: Callable = operator.and_) -> Pattern:
    pass


def parse_url(value: Union[httpx.URL, str, RawURL]) -> httpx.URL:
    pass


def parse_url_patterns(
    url: Optional[URLPatternTypes], exact: bool = True
) -> Dict[str, Pattern]:
    pass


def merge_patterns(pattern: Pattern, **bases: Pattern) -> Pattern:
    pass
