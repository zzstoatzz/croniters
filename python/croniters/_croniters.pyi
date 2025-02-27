"""Type stubs for croniters Rust extension."""

from __future__ import annotations

from typing import Any, TypeAlias

__version__: str

MINUTE_FIELD: int
HOUR_FIELD: int
DAY_FIELD: int
MONTH_FIELD: int
DOW_FIELD: int
SECOND_FIELD: int
YEAR_FIELD: int

RANGES: list[tuple[int, int]]
DAYS: list[int]
M_ALPHAS: dict[str, int]
DOW_ALPHAS: dict[str, int]
UNIX_FIELDS: list[int]
SECOND_FIELDS: list[int]
YEAR_FIELDS: list[int]
CRON_FIELDS: dict[str | int, list[int]]

WEEKDAYS: str
MONTHS: str

UNIX_CRON_LEN: int
SECOND_CRON_LEN: int
YEAR_CRON_LEN: int

VALID_LEN_EXPRESSION: set[int]

LEN_MEANS_ALL: list[int]

def is_32bit() -> bool:
    """Detect if Python is running in 32-bit mode.

    see https://github.com/python/cpython/issues/101069 for details

    Returns:
        True if running on 32-bit Python, False for 64-bit.
    """
    pass

def is_leap(year: int) -> bool:
    """Check if a year is a leap year.

    Args:
        year: The year to check.
    """
    pass

class HashExpander:
    def __init__(self, cronit: Any) -> None:
        pass

    def do(
        self,
        idx: int,
        hash_type: str = 'h',
        hash_id: bytes | None = None,
        range_end: int | None = None,
        range_begin: int | None = None,
    ) -> int:
        pass

    def match(
        self, efl: Any, idx: int, expr: str, hash_id: bytes | None = None, **kw: Any
    ) -> bool:
        pass

    def expand(
        self,
        efl: Any,
        idx: int,
        expr: str,
        hash_id: bytes | None = None,
        match: str | None = None,
        **kw: Any,
    ) -> str:
        pass

ExpanderType: TypeAlias = HashExpander
EXPANDERS: dict[str, ExpanderType]
