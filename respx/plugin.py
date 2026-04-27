from typing import cast

import pytest

import respx

from .router import MockRouter


def pytest_configure(config):
    pass


@pytest.fixture
def respx_mock(request):
    pass
