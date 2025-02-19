import os
import time
from collections.abc import Generator
from datetime import datetime

import pytest
from croniters import croniter


@pytest.fixture
def timezone_setup() -> Generator[tuple[datetime, list[datetime]], None, None]:
    orig_time = os.environ.setdefault('TZ', '')
    base = datetime(2024, 1, 25, 4, 46)
    expected = [
        datetime(2024, 1, 25, 4, 50),
        datetime(2024, 1, 25, 4, 55),
        datetime(2024, 1, 25, 5, 0),
    ]

    yield base, expected

    if not orig_time:
        del os.environ['TZ']
    else:
        os.environ['TZ'] = orig_time
    time.tzset()


@pytest.mark.parametrize('tz', ['UTC', 'UTC-8'])
def test_dst_138(timezone_setup, tz):
    """Test DST handling - see issue #138"""
    base, expected = timezone_setup

    os.environ['TZ'] = tz
    time.tzset()

    itr = croniter('*/5 * * * *', base)
    result = [itr.get_next(datetime) for _ in range(3)]
    assert result == expected
