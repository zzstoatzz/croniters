from datetime import datetime, timedelta

import pytest
from croniters import croniter


@pytest.fixture
def epoch():
    return datetime(2020, 1, 1, 0, 0)


def test_random(epoch):
    """Test random definition"""
    obj = croniter('R R * * *', epoch)
    result_1 = obj.get_next(datetime)
    assert result_1 >= datetime(2020, 1, 1, 0, 0)
    assert result_1 <= datetime(2020, 1, 1, 0, 0) + timedelta(days=1)
    result_2 = obj.get_next(datetime)
    assert result_2 >= datetime(2020, 1, 2, 0, 0)
    assert result_2 <= datetime(2020, 1, 2, 0, 0) + timedelta(days=1)


def test_random_range(epoch):
    """Test random definition within a range"""
    obj = croniter('R R R(10-20) * *', epoch)
    result_1 = obj.get_next(datetime)
    assert result_1 >= datetime(2020, 1, 10, 0, 0)
    assert result_1 <= datetime(2020, 1, 10, 0, 0) + timedelta(days=11)
    result_2 = obj.get_next(datetime)
    assert result_2 >= datetime(2020, 2, 10, 0, 0)
    assert result_2 <= datetime(2020, 2, 10, 0, 0) + timedelta(days=11)


def test_random_float(epoch: datetime):
    """Test random definition, float result"""
    obj = croniter('R R * * *', epoch)
    result_1 = obj.get_next(float)
    assert isinstance(result_1, float)
    assert result_1 >= 1577836800.0
    assert result_1 <= 1577836800.0 + (60 * 60 * 24)
    result_2 = obj.get_next(float)
    assert isinstance(result_2, float)
    assert result_2 >= 1577923200.0
    assert result_2 <= 1577923200.0 + (60 * 60 * 24)


def test_random_with_year(epoch):
    """Test random with year range"""
    obj = croniter('* * * * * * R(2025-2030)', epoch)
    result = obj.get_next(datetime)
    assert result.year >= 2025
    assert result.year <= 2030
