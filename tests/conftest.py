"""Shared pytest configuration and fixtures for Purple's test suite.

testpaths, pythonpath (src/), and asyncio_mode are configured in pyproject.toml.
Project-wide fixtures belong here; module-specific ones in tests/<area>/conftest.py.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def allow_approver():
    """An approver that confirms any action — handy for exercising gated tools."""

    async def _approve(_name, _args):
        return True

    return _approve


@pytest.fixture
def deny_approver():
    """An approver that rejects every confirmation request."""

    async def _deny(_name, _args):
        return False

    return _deny
