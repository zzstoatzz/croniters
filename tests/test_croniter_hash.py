import random
import uuid
from datetime import datetime, timedelta

import pytest
from croniters import CroniterBadCronError, CroniterNotAlphaError, croniter


# Convert base class setup into fixtures
@pytest.fixture
def hash_setup():
    return {'epoch': datetime(2020, 1, 1, 0, 0), 'hash_id': 'hello'}


# Helper function to replace the _test_iter method
def check_iter(
    definition, expectations, delta, epoch=None, hash_id=None, next_type=None
):
    if epoch is None:
        epoch = datetime(2020, 1, 1, 0, 0)
    if hash_id is None:
        hash_id = 'hello'
    if next_type is None:
        next_type = datetime
    if not isinstance(expectations, (list, tuple)):
        expectations = (expectations,)

    obj = croniter(definition, epoch, hash_id=hash_id)
    testval = obj.get_next(next_type)
    assert testval in expectations
    if delta is not None:
        assert obj.get_next(next_type) == testval + delta


# Convert test methods to functions
def test_hash_hourly(hash_setup):
    """Test manually-defined hourly"""
    check_iter('H * * * *', datetime(2020, 1, 1, 0, 10), timedelta(hours=1))


def test_hash_daily(hash_setup):
    """Test manually-defined daily"""
    check_iter('H H * * *', datetime(2020, 1, 1, 11, 10), timedelta(days=1))


def test_hash_weekly(hash_setup):
    """Test manually-defined weekly"""
    # croniter 1.0.5 changes the defined weekly range from (0, 6)
    # to (0, 7), to match cron's behavior that Sunday is 0 or 7.
    # This changes the hash, so test for either.
    check_iter(
        'H H * * H',
        (datetime(2020, 1, 3, 11, 10), datetime(2020, 1, 5, 11, 10)),
        timedelta(weeks=1),
    )


def test_hash_monthly(hash_setup):
    """Test manually-defined monthly"""
    check_iter('H H H * *', datetime(2020, 1, 1, 11, 10), timedelta(days=31))


def test_hash_yearly(hash_setup):
    """Test manually-defined yearly"""
    check_iter('H H H H *', datetime(2020, 9, 1, 11, 10), timedelta(days=365))


def test_hash_second(hash_setup):
    """Test seconds

    If a sixth field is provided, seconds are included in the datetime()
    """
    check_iter('H H * * * H', datetime(2020, 1, 1, 11, 10, 32), timedelta(days=1))


def test_hash_year(hash_setup):
    """Test years

    provide a seventh field as year
    """
    check_iter('H H * * * H H', datetime(2066, 1, 1, 11, 10, 32), timedelta(days=1))


def test_hash_id_change(hash_setup):
    """Test a different hash_id returns different results given same definition and epoch"""
    check_iter('H H * * *', datetime(2020, 1, 1, 11, 10), timedelta(days=1))
    check_iter(
        'H H * * *',
        datetime(2020, 1, 1, 0, 24),
        timedelta(days=1),
        hash_id='different id',
    )


def test_hash_epoch_change(hash_setup):
    """Test a different epoch returns different results given same definition and hash_id"""
    check_iter('H H * * *', datetime(2020, 1, 1, 11, 10), timedelta(days=1))
    check_iter(
        'H H * * *',
        datetime(2011, 11, 12, 11, 10),
        timedelta(days=1),
        epoch=datetime(2011, 11, 11, 11, 11),
    )


def test_hash_range(hash_setup):
    """Test a hashed range definition"""
    check_iter('H H H(3-5) * *', datetime(2020, 1, 5, 11, 10), timedelta(days=31))
    check_iter(
        'H H * * * 0 H(2025-2030)', datetime(2029, 1, 1, 11, 10), timedelta(days=1)
    )


def test_hash_division(hash_setup):
    """Test a hashed division definition"""
    check_iter('H H/3 * * *', datetime(2020, 1, 1, 2, 10), timedelta(hours=3))
    check_iter(
        'H H H H * H H/2', datetime(2020, 9, 1, 11, 10, 32), timedelta(days=365 * 2)
    )


def test_hash_range_division(hash_setup):
    """Test a hashed range + division definition"""
    check_iter(
        'H(30-59)/10 H * * *', datetime(2020, 1, 1, 11, 30), timedelta(minutes=10)
    )


def test_hash_invalid_range(hash_setup):
    """Test validation logic for range_begin and range_end values"""
    try:
        check_iter(
            'H(11-10) H * * *', datetime(2020, 1, 1, 11, 31), timedelta(minutes=10)
        )
    except CroniterBadCronError as ex:
        assert str(ex) == 'Range end must be greater than range begin'


def test_hash_id_bytes(hash_setup):
    """Test hash_id as a bytes object"""
    check_iter(
        'H H * * *',
        datetime(2020, 1, 1, 14, 53),
        timedelta(days=1),
        hash_id=b'\x01\x02\x03\x04',
    )


def test_hash_float(hash_setup):
    """Test result as a float object"""
    check_iter('H H * * *', 1577877000.0, (60 * 60 * 24), next_type=float)


def test_invalid_definition(hash_setup):
    """Test an invalid definition raises CroniterNotAlphaError"""
    with pytest.raises(CroniterNotAlphaError):
        croniter('X X * * *', hash_setup['epoch'], hash_id=hash_setup['hash_id'])


def test_invalid_hash_id_type(hash_setup):
    """Test an invalid hash_id type raises TypeError"""
    with pytest.raises(TypeError):
        croniter('H H * * *', hash_setup['epoch'], hash_id={1: 2})


def test_invalid_divisor(hash_setup):
    """Test an invalid divisor type raises CroniterBadCronError"""
    with pytest.raises(CroniterBadCronError):
        croniter('* * H/0 * *', hash_setup['epoch'], hash_id=hash_setup['hash_id'])


def test_hash_word_midnight(hash_setup):
    """Test built-in @midnight

    @midnight is actually up to 3 hours after midnight, not exactly midnight
    """
    check_iter('@midnight', datetime(2020, 1, 1, 2, 10, 32), timedelta(days=1))


def test_hash_word_hourly(hash_setup):
    """Test built-in @hourly"""
    check_iter('@hourly', datetime(2020, 1, 1, 0, 10, 32), timedelta(hours=1))


def test_hash_word_daily(hash_setup):
    """Test built-in @daily"""
    check_iter('@daily', datetime(2020, 1, 1, 11, 10, 32), timedelta(days=1))


def test_hash_word_weekly(hash_setup):
    """Test built-in @weekly"""
    # croniter 1.0.5 changes the defined weekly range from (0, 6)
    # to (0, 7), to match cron's behavior that Sunday is 0 or 7.
    # This changes the hash, so test for either.
    check_iter(
        '@weekly',
        (datetime(2020, 1, 3, 11, 10, 32), datetime(2020, 1, 5, 11, 10, 32)),
        timedelta(weeks=1),
    )


def test_hash_word_monthly(hash_setup):
    """Test built-in @monthly"""
    check_iter('@monthly', datetime(2020, 1, 1, 11, 10, 32), timedelta(days=31))


def test_hash_word_yearly(hash_setup):
    """Test built-in @yearly"""
    check_iter('@yearly', datetime(2020, 9, 1, 11, 10, 32), timedelta(days=365))


def test_hash_word_annually(hash_setup):
    """Test built-in @annually

    @annually is the same as @yearly
    """
    obj_annually = croniter(
        '@annually', hash_setup['epoch'], hash_id=hash_setup['hash_id']
    )
    obj_yearly = croniter('@yearly', hash_setup['epoch'], hash_id=hash_setup['hash_id'])
    assert obj_annually.get_next(datetime) == obj_yearly.get_next(datetime)
    assert obj_annually.get_next(datetime) == obj_yearly.get_next(datetime)


@pytest.fixture
def hash_ids():
    _rd = random.Random()
    _rd.seed(100)
    return [uuid.UUID(int=_rd.getrandbits(128)).bytes for _ in range(350)]


# Minutes expander tests
def test_expand_minutes(hash_ids):
    minutes = set()
    expression = 'H * * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        minutes.add(expanded[0][0][0])
    assert len(minutes) == 60
    assert min(minutes) == 0
    assert max(minutes) == 59


def test_expand_minutes_range_2_minutes(hash_ids):
    minutes = set()
    expression = 'H/2 * * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _minutes = expanded[0][0]
        assert len(_minutes) == 30
        minutes.update(_minutes)
    assert len(minutes) == 60
    assert min(minutes) == 0
    assert max(minutes) == 59


def test_expand_minutes_range_3_minutes(hash_ids):
    minutes = set()
    expression = 'H/3 * * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _minutes = expanded[0][0]
        assert len(_minutes) == 20
        minutes.update(_minutes)
    assert len(minutes) == 60
    assert min(minutes) == 0
    assert max(minutes) == 59


def test_expand_minutes_range_15_minutes(hash_ids):
    minutes = set()
    expression = 'H/15 * * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _minutes = expanded[0][0]
        assert len(_minutes) == 4
        minutes.update(_minutes)
    assert len(minutes) == 60
    assert min(minutes) == 0
    assert max(minutes) == 59


def test_expand_minutes_with_full_range(hash_ids):
    minutes = set()
    expression = 'H(0-59) * * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        minutes.add(expanded[0][0][0])
    assert len(minutes) == 60
    assert min(minutes) == 0
    assert max(minutes) == 59


# Hours expander tests
def test_expand_hours(hash_ids):
    hours = set()
    expression = 'H H * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        hours.add(expanded[0][1][0])
    assert len(hours) == 24
    assert min(hours) == 0
    assert max(hours) == 23


def test_expand_hours_range_every_2_hours(hash_ids):
    hours = set()
    expression = 'H H/2 * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _hours = expanded[0][1]
        assert len(_hours) == 12
        hours.update(_hours)
    assert len(hours) == 24
    assert min(hours) == 0
    assert max(hours) == 23


def test_expand_hours_range_4_hours(hash_ids):
    hours = set()
    expression = 'H H/4 * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _hours = expanded[0][1]
        assert len(_hours) == 6
        hours.update(_hours)
    assert len(hours) == 24
    assert min(hours) == 0
    assert max(hours) == 23


def test_expand_hours_range_8_hours(hash_ids):
    hours = set()
    expression = 'H H/8 * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _hours = expanded[0][1]
        assert len(_hours) == 3
        hours.update(_hours)
    assert len(hours) == 24
    assert min(hours) == 0
    assert max(hours) == 23


def test_expand_hours_range_10_hours(hash_ids):
    hours = set()
    expression = 'H H/10 * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _hours = expanded[0][1]
        assert len(_hours) in {2, 3}
        hours.update(_hours)
    assert len(hours) == 24
    assert min(hours) == 0
    assert max(hours) == 23


def test_expand_hours_range_12_hours(hash_ids):
    hours = set()
    expression = 'H H/12 * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _hours = expanded[0][1]
        assert len(_hours) == 2
        hours.update(_hours)
    assert len(hours) == 24
    assert min(hours) == 0
    assert max(hours) == 23


def test_expand_hours_with_full_range(hash_ids):
    minutes = set()
    expression = '* H(0-23) * * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        minutes.add(expanded[0][1][0])
    assert len(minutes) == 24
    assert min(minutes) == 0
    assert max(minutes) == 23


# Month days expander tests
def test_expand_month_days(hash_ids):
    month_days = set()
    expression = 'H H H * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        month_days.add(expanded[0][2][0])
    assert len(month_days) == 31
    assert min(month_days) == 1
    assert max(month_days) == 31


def test_expand_month_days_range_2_days(hash_ids):
    month_days = set()
    expression = '0 0 H/2 * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _days = expanded[0][2]
        assert len(_days) in {15, 16}
        month_days.update(_days)
    assert len(month_days) == 31
    assert min(month_days) == 1
    assert max(month_days) == 31


def test_expand_month_days_range_5_days(hash_ids):
    month_days = set()
    expression = 'H H H/5 * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _days = expanded[0][2]
        assert len(_days) in {6, 7}
        month_days.update(_days)
    assert len(month_days) == 31
    assert min(month_days) == 1
    assert max(month_days) == 31


def test_expand_month_days_range_12_days(hash_ids):
    month_days = set()
    expression = 'H H H/12 * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _days = expanded[0][2]
        assert len(_days) in {2, 3}
        month_days.update(_days)
    assert len(month_days) == 31
    assert min(month_days) == 1
    assert max(month_days) == 31


def test_expand_month_days_with_full_range(hash_ids):
    month_days = set()
    expression = '* * H(1-31) * *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        month_days.add(expanded[0][2][0])
    assert len(month_days) == 31
    assert min(month_days) == 1
    assert max(month_days) == 31


# Month expander tests
def test_expand_months(hash_ids):
    months = set()
    expression = 'H H * H *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        months.add(expanded[0][3][0])
    assert len(months) == 12
    assert min(months) == 1
    assert max(months) == 12


def test_expand_month_days_range_2_months(hash_ids):
    months = set()
    expression = 'H H * H/2 *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _months = expanded[0][3]
        assert len(_months) == 6
        months.update(_months)
    assert len(months) == 12
    assert min(months) == 1
    assert max(months) == 12


def test_expand_month_days_range_3_months(hash_ids):
    months = set()
    expression = 'H H * H/3 *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _months = expanded[0][3]
        assert len(_months) == 4
        months.update(_months)
    assert len(months) == 12
    assert min(months) == 1
    assert max(months) == 12


def test_expand_month_days_range_5_months(hash_ids):
    months = set()
    expression = 'H H * H/5 *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _months = expanded[0][3]
        assert len(_months) in {2, 3}
        months.update(_months)
    assert len(months) == 12
    assert min(months) == 1
    assert max(months) == 12


def test_expand_months_with_full_range(hash_ids):
    months = set()
    expression = '* * * H(1-12) *'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        months.add(expanded[0][3][0])
    assert len(months) == 12
    assert min(months) == 1
    assert max(months) == 12


# Week days expander tests
def test_expand_week_days(hash_ids):
    week_days = set()
    expression = 'H H * * H'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        week_days.add(expanded[0][4][0])
    assert len(week_days) == 7
    assert min(week_days) == 0
    assert max(week_days) == 6


def test_expand_week_days_range_2_days(hash_ids):
    days = set()
    expression = 'H H * * H/2'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _days = expanded[0][4]
        assert len(_days) in {3, 4}
        days.update(_days)
    assert len(days) == 7
    assert min(days) == 0
    assert max(days) == 6


def test_expand_week_days_range_4_days(hash_ids):
    days = set()
    expression = 'H H * * H/4'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        _days = expanded[0][4]
        assert len(_days) in {1, 2}
        days.update(_days)
    assert len(days) == 7
    assert min(days) == 0
    assert max(days) == 6


def test_expand_week_days_with_full_range(hash_ids):
    days = set()
    expression = '* * * * H(0-6)'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        days.add(expanded[0][4][0])
    assert len(days) == 7
    assert min(days) == 0
    assert max(days) == 6


# Years expander tests
def test_expand_years_by_division(hash_ids):
    years = set()
    year_min, year_max = croniter.RANGES[6]
    expression = '* * * * * * H/10'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        assert len(expanded[0][6]) == 13
        years.update(expanded[0][6])
    assert len(years) == year_max - year_min + 1
    assert min(years) == year_min
    assert max(years) == year_max


def test_expand_years_by_range(hash_ids):
    years = set()
    expression = '* * * * * * H(2020-2030)'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        years.add(expanded[0][6][0])
    assert len(years) == 11
    assert min(years) == 2020
    assert max(years) == 2030


def test_expand_years_by_range_and_division(hash_ids):
    years = set()
    expression = '* * * * * * H(2020-2050)/10'
    for hash_id in hash_ids:
        expanded = croniter.expand(expression, hash_id=hash_id)
        years.update(expanded[0][6])
    assert len(years) == 31
    assert min(years) == 2020
    assert max(years) == 2050


if __name__ == '__main__':
    pytest.main()
