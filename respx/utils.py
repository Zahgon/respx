import email
from collections import defaultdict
from datetime import datetime
from email.message import Message
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from urllib.parse import parse_qsl

import httpx


class MultiItems(defaultdict):
    def __init__(self, values: Optional[Iterable[Tuple[str, Any]]] = None) -> None:
        pass

    def get_list(self, key: str) -> List[Any]:
        pass

    def multi_items(self) -> List[Tuple[str, str]]:
        pass

    def append(self, key: str, value: Any) -> None:
        pass


def _parse_multipart_form_data(
    content: bytes, *, content_type: str, encoding: str
) -> Tuple[MultiItems, MultiItems]:
    pass


def _parse_urlencoded_data(content: bytes, *, encoding: str) -> MultiItems:
    pass


def decode_data(request: httpx.Request) -> Tuple[MultiItems, MultiItems]:
    pass


Self = TypeVar("Self", bound="SetCookie")


class SetCookie(
    NamedTuple(
        "SetCookie",
        [
            ("header_name", Literal["Set-Cookie"]),
            ("header_value", str),
        ],
    )
):
    def __new__(
        cls: Type[Self],
        name: str,
        value: str,
        *,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        expires: Optional[Union[str, datetime]] = None,
        max_age: Optional[int] = None,
        http_only: bool = False,
        same_site: Optional[Literal["Strict", "Lax", "None"]] = None,
        secure: bool = False,
        partitioned: bool = False,
    ) -> Self:
        """
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#syntax
        """
        attrs: Dict[str, Union[str, bool]] = {name: value}
        if path is not None:
            attrs["Path"] = path
        if domain is not None:
            attrs["Domain"] = domain
        if expires is not None:
            if isinstance(expires, datetime):  # pragma: no branch
                expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
            attrs["Expires"] = expires
        if max_age is not None:
            attrs["Max-Age"] = str(max_age)
        if http_only:
            attrs["HttpOnly"] = True
        if same_site is not None:
            attrs["SameSite"] = same_site
            if same_site == "None":  # pragma: no branch
                secure = True
        if secure:
            attrs["Secure"] = True
        if partitioned:
            attrs["Partitioned"] = True

        string = "; ".join(
            _name if _value is True else f"{_name}={_value}"
            for _name, _value in attrs.items()
        )
        self = super().__new__(cls, "Set-Cookie", string)
        return self
