"""Type stubs for croniters Rust extension."""

from __future__ import annotations

__version__: str

MINUTE_FIELD: int
HOUR_FIELD: int
DAY_FIELD: int
MONTH_FIELD: int
DOW_FIELD: int
SECOND_FIELD: int
YEAR_FIELD: int

M_ALPHAS: dict[str, int]
DOW_ALPHAS: dict[str, int]
UNIX_FIELDS: list[int]
SECOND_FIELDS: list[int]
YEAR_FIELDS: list[int]
CRON_FIELDS: dict[str | int, list[int]]

def is_32bit() -> bool:
    """Detect if Python is running in 32-bit mode.

    Returns:
        True if running on 32-bit Python, False for 64-bit.
    """
    pass
