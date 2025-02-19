from datetime import datetime

import pytest
import pytz
from croniters import (
    CroniterBadCronError,
    CroniterBadDateError,
    CroniterBadTypeRangeError,
    croniter,
    croniter_range,
)


class mydatetime(datetime):
    """Custom datetime class for testing"""

    pass


def test_1day_step():
    start = datetime(2016, 12, 2)
    stop = datetime(2016, 12, 10)
    fwd = list(croniter_range(start, stop, '0 0 * * *'))
    assert len(fwd) == 9
    assert fwd[0] == start
    assert fwd[-1] == stop
    # Test the same, but in reverse
    rev = list(croniter_range(stop, start, '0 0 * * *'))
    assert len(rev) == 9
    # Ensure forward/reverse are a mirror image
    rev.reverse()
    assert fwd == rev


def test_1day_step_no_ends():
    # Test without ends (exclusive)
    start = datetime(2016, 12, 2)
    stop = datetime(2016, 12, 10)
    fwd = list(croniter_range(start, stop, '0 0 * * *', exclude_ends=True))
    assert len(fwd) == 7
    assert fwd[0] != start
    assert fwd[-1] != stop
    # Test the same, but in reverse
    rev = list(croniter_range(stop, start, '0 0 * * *', exclude_ends=True))
    assert len(rev) == 7
    assert fwd[0] != stop
    assert fwd[-1] != start


def test_1month_step():
    start = datetime(1982, 1, 1)
    stop = datetime(1983, 12, 31)
    res = list(croniter_range(start, stop, '0 0 1 * *'))
    assert len(res) == 24
    assert res[0] == start
    assert res[5].day == 1
    assert res[-1] == datetime(1983, 12, 1)


def test_1minute_step_float():
    start = datetime(2000, 1, 1, 0, 0)
    stop = datetime(2000, 1, 1, 0, 1)
    res = list(croniter_range(start, stop, '* * * * *', ret_type=float))
    assert len(res) == 2
    assert res[0] == 946684800.0
    assert res[-1] - res[0] == 60


def test_auto_ret_type():
    data = [
        (datetime(2019, 1, 1), datetime(2020, 1, 1), datetime),
        (1552252218.0, 1591823311.0, float),
    ]
    for start, stop, rtype in data:
        ret = list(croniter_range(start, stop, '0 0 * * *'))
        assert isinstance(ret[0], rtype)


def test_input_type_exceptions():
    dt_start1 = datetime(2019, 1, 1)
    dt_stop1 = datetime(2020, 1, 1)
    f_start1 = 1552252218.0
    f_stop1 = 1591823311.0
    # Mix start/stop types
    with pytest.raises(TypeError):
        list(croniter_range(dt_start1, f_stop1, '0 * * * *'), ret_type=datetime)
    with pytest.raises(TypeError):
        list(croniter_range(f_start1, dt_stop1, '0 * * * *'))


def test_timezone_dst():
    """Test across DST transition, which technically is a timezone change."""
    tz = pytz.timezone('US/Eastern')
    start = tz.localize(datetime(2020, 10, 30))
    stop = tz.localize(datetime(2020, 11, 10))
    res = list(croniter_range(start, stop, '0 0 * * *'))
    assert res[0].tzinfo != res[-1].tzinfo
    assert len(res) == 12


def test_extra_hour_day_prio():
    def datetime_tz(*args, **kw):
        """Defined this in another branch. single-use-version"""
        tzinfo = kw.pop('tzinfo')
        return tzinfo.localize(datetime(*args))

    tz = pytz.timezone('US/Eastern')
    cron = '0 3 * * *'
    start = datetime_tz(2020, 3, 7, tzinfo=tz)
    end = datetime_tz(2020, 3, 11, tzinfo=tz)
    ret = [i.isoformat() for i in croniter_range(start, end, cron)]
    assert ret == [
        '2020-03-07T03:00:00-05:00',
        '2020-03-08T03:00:00-04:00',
        '2020-03-09T03:00:00-04:00',
        '2020-03-10T03:00:00-04:00',
    ]


def test_issue145_getnext():
    # Example of quarterly event cron schedule
    start = datetime(2020, 9, 24)
    cron = '0 13 8 1,4,7,10 wed'
    with pytest.raises(CroniterBadDateError):
        it = croniter(cron, start, day_or=False, max_years_between_matches=1)
        it.get_next()
    # New functionality (0.3.35) allowing croniter to find sparse matches of cron patterns across multiple years
    it = croniter(cron, start, day_or=False, max_years_between_matches=5)
    assert it.get_next(datetime) == datetime(2025, 1, 8, 13)


def test_issue145_range():
    cron = '0 13 8 1,4,7,10 wed'
    matches = list(
        croniter_range(datetime(2020, 1, 1), datetime(2020, 12, 31), cron, day_or=False)
    )
    assert len(matches) == 3
    assert matches[0] == datetime(2020, 1, 8, 13)
    assert matches[1] == datetime(2020, 4, 8, 13)
    assert matches[2] == datetime(2020, 7, 8, 13)

    # No matches within this range; therefore expect empty list
    matches = list(
        croniter_range(
            datetime(2020, 9, 30), datetime(2020, 10, 30), cron, day_or=False
        )
    )
    assert len(matches) == 0


def test_croniter_range_derived_class():
    # trivial example extending croniter
    class croniter_nosec(croniter):
        """Like croniter, but it forbids second-level cron expressions."""

        @classmethod
        def expand(cls, expr_format, *args, **kwargs):
            if len(expr_format.split()) == 6:
                raise CroniterBadCronError("Expected 'min hour day mon dow'")
            return croniter.expand(expr_format, *args, **kwargs)

    cron = '0 13 8 1,4,7,10 wed'
    matches = list(
        croniter_range(
            datetime(2020, 1, 1),
            datetime(2020, 12, 31),
            cron,
            day_or=False,
            _croniter=croniter_nosec,
        )
    )
    assert len(matches) == 3

    cron = '0 1 8 1,15,L wed 15,45'
    with pytest.raises(CroniterBadCronError):
        # Should fail using the custom class that forbids the seconds expression
        croniter_nosec(cron)

    with pytest.raises(CroniterBadCronError):
        # Should similarly fail because the custom class rejects seconds expr
        i = croniter_range(
            datetime(2020, 1, 1),
            datetime(2020, 12, 31),
            cron,
            _croniter=croniter_nosec,
        )
        next(i)


def test_dt_types():
    start = mydatetime(2020, 9, 24)
    stop = datetime(2020, 9, 28)
    try:
        list(croniter_range(start, stop, '0 0 * * *'))
    except CroniterBadTypeRangeError:
        pytest.fail('should not be triggered')


def test_configure_second_location():
    start = datetime(2016, 12, 2, 0, 0, 0)
    stop = datetime(2016, 12, 2, 0, 1, 0)
    fwd = list(croniter_range(start, stop, '*/20 * * * * *', second_at_beginning=True))
    assert len(fwd) == 4
    assert fwd[0] == start
    assert fwd[-1] == stop


def test_year_range():
    start = datetime(2010, 1, 1)
    stop = datetime(2030, 1, 1)
    fwd = list(croniter_range(start, stop, '0 0 1 1 ? 0 2020-2024,2028'))
    assert len(fwd) == 6
    assert fwd[0] == datetime(2020, 1, 1)
    assert fwd[-1] == datetime(2028, 1, 1)
