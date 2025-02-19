from datetime import datetime, timedelta
from functools import partial
from time import sleep

import dateutil.tz
import pytest
import pytz
from croniters import (
    VALID_LEN_EXPRESSION,
    CroniterBadCronError,
    CroniterBadDateError,
    CroniterNotAlphaError,
    CroniterUnsupportedSyntaxError,
    croniter,
    datetime_to_timestamp,
)


def assert_equal(a, b):
    assert a == b


def assert_raises(exception, func, *args, **kwargs):
    with pytest.raises(exception):
        func(*args, **kwargs)


def assert_true(condition):
    assert condition


def assert_false(condition):
    assert not condition


class TestCroniter:
    def testSecondSec(self):
        base = datetime(2012, 4, 6, 13, 26, 10)
        itr = croniter('* * * * * 15,25', base)
        n = itr.get_next(datetime)
        assert_equal(15, n.second)
        n = itr.get_next(datetime)
        assert_equal(25, n.second)
        n = itr.get_next(datetime)
        assert_equal(15, n.second)
        assert_equal(27, n.minute)

    def testSecond(self):
        base = datetime(2012, 4, 6, 13, 26, 10)
        itr = croniter('*/1 * * * * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(base.year, n1.year)
        assert_equal(base.month, n1.month)
        assert_equal(base.day, n1.day)
        assert_equal(base.hour, n1.hour)
        assert_equal(base.minute, n1.minute)
        assert_equal(base.second + 1, n1.second)

    def testSecondRepeat(self):
        base = datetime(2012, 4, 6, 13, 26, 36)
        itr = croniter('* * * * * */15', base)
        n1 = itr.get_next(datetime)
        n2 = itr.get_next(datetime)
        n3 = itr.get_next(datetime)
        assert_equal(base.year, n1.year)
        assert_equal(base.month, n1.month)
        assert_equal(base.day, n1.day)
        assert_equal(base.hour, n1.hour)
        assert_equal(base.minute, n1.minute)
        assert_equal(45, n1.second)
        assert_equal(base.year, n2.year)
        assert_equal(base.month, n2.month)
        assert_equal(base.day, n2.day)
        assert_equal(base.hour, n2.hour)
        assert_equal(base.minute + 1, n2.minute)
        assert_equal(0, n2.second)
        assert_equal(base.year, n3.year)
        assert_equal(base.month, n3.month)
        assert_equal(base.day, n3.day)
        assert_equal(base.hour, n3.hour)
        assert_equal(base.minute + 1, n3.minute)
        assert_equal(15, n3.second)

    def testMinute(self):
        # minute asterisk
        base = datetime(2010, 1, 23, 12, 18)
        itr = croniter('*/1 * * * *', base)
        n1 = itr.get_next(datetime)  # 19
        assert_equal(base.year, n1.year)
        assert_equal(base.month, n1.month)
        assert_equal(base.day, n1.day)
        assert_equal(base.hour, n1.hour)
        assert_equal(base.minute, n1.minute - 1)
        for i in range(39):  # ~ 58
            itr.get_next()
        n2 = itr.get_next(datetime)
        assert_equal(n2.minute, 59)
        n3 = itr.get_next(datetime)
        assert_equal(n3.minute, 0)
        assert_equal(n3.hour, 13)

        itr = croniter('*/5 * * * *', base)
        n4 = itr.get_next(datetime)
        assert_equal(n4.minute, 20)
        for i in range(6):
            itr.get_next()
        n5 = itr.get_next(datetime)
        assert_equal(n5.minute, 55)
        n6 = itr.get_next(datetime)
        assert_equal(n6.minute, 0)
        assert_equal(n6.hour, 13)

    def testHour(self):
        base = datetime(2010, 1, 24, 12, 2)
        itr = croniter('0 */3 * * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.hour, 15)
        assert_equal(n1.minute, 0)
        for i in range(2):
            itr.get_next()
        n2 = itr.get_next(datetime)
        assert_equal(n2.hour, 0)
        assert_equal(n2.day, 25)

    def testDay(self):
        base = datetime(2010, 2, 24, 12, 9)
        itr = croniter('0 0 */3 * *', base)
        n1 = itr.get_next(datetime)
        # 1 4 7 10 13 16 19 22 25 28
        assert_equal(n1.day, 25)
        n2 = itr.get_next(datetime)
        assert_equal(n2.day, 28)
        n3 = itr.get_next(datetime)
        assert_equal(n3.day, 1)
        assert_equal(n3.month, 3)

        # test leap year
        base = datetime(1996, 2, 27)
        itr = croniter('0 0 * * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.day, 28)
        assert_equal(n1.month, 2)
        n2 = itr.get_next(datetime)
        assert_equal(n2.day, 29)
        assert_equal(n2.month, 2)

        base2 = datetime(2000, 2, 27)
        itr2 = croniter('0 0 * * *', base2)
        n3 = itr2.get_next(datetime)
        assert_equal(n3.day, 28)
        assert_equal(n3.month, 2)
        n4 = itr2.get_next(datetime)
        assert_equal(n4.day, 29)
        assert_equal(n4.month, 2)

    def testDay2(self):
        base3 = datetime(2024, 2, 28)
        itr2 = croniter('* * 29 2 *', base3)
        n3 = itr2.get_prev(datetime)
        assert_equal(n3.year, 2020)
        assert_equal(n3.month, 2)
        assert_equal(n3.day, 29)

    def testWeekDay(self):
        base = datetime(2010, 2, 25)
        itr = croniter('0 0 * * sat', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.isoweekday(), 6)
        assert_equal(n1.day, 27)
        n2 = itr.get_next(datetime)
        assert_equal(n2.isoweekday(), 6)
        assert_equal(n2.day, 6)
        assert_equal(n2.month, 3)

        base = datetime(2010, 1, 25)
        itr = croniter('0 0 1 * wed', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.month, 1)
        assert_equal(n1.day, 27)
        assert_equal(n1.year, 2010)
        n2 = itr.get_next(datetime)
        assert_equal(n2.month, 2)
        assert_equal(n2.day, 1)
        assert_equal(n2.year, 2010)
        n3 = itr.get_next(datetime)
        assert_equal(n3.month, 2)
        assert_equal(n3.day, 3)
        assert_equal(n3.year, 2010)

    def testNthWeekDay(self):
        base = datetime(2010, 2, 25)
        itr = croniter('0 0 * * sat#1', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.isoweekday(), 6)
        assert_equal(n1.day, 6)
        assert_equal(n1.month, 3)
        n2 = itr.get_next(datetime)
        assert_equal(n2.isoweekday(), 6)
        assert_equal(n2.day, 3)
        assert_equal(n2.month, 4)

        base = datetime(2010, 1, 25)
        itr = croniter('0 0 * * wed#5', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.month, 3)
        assert_equal(n1.day, 31)
        assert_equal(n1.year, 2010)
        n2 = itr.get_next(datetime)
        assert_equal(n2.month, 6)
        assert_equal(n2.day, 30)
        assert_equal(n2.year, 2010)
        n3 = itr.get_next(datetime)
        assert_equal(n3.month, 9)
        assert_equal(n3.day, 29)
        assert_equal(n3.year, 2010)

    def testWeekDayDayAnd(self):
        base = datetime(2010, 1, 25)
        itr = croniter('0 0 1 * mon', base, day_or=False)
        n1 = itr.get_next(datetime)
        assert_equal(n1.month, 2)
        assert_equal(n1.day, 1)
        assert_equal(n1.year, 2010)
        n2 = itr.get_next(datetime)
        assert_equal(n2.month, 3)
        assert_equal(n2.day, 1)
        assert_equal(n2.year, 2010)
        n3 = itr.get_next(datetime)
        assert_equal(n3.month, 11)
        assert_equal(n3.day, 1)
        assert_equal(n3.year, 2010)

    def testDomDowVixieCronBug(self):
        expr = '0 16 */2 * sat'

        # UNION OF "every odd-numbered day" and "every Saturday"
        itr = croniter(expr, start_time=datetime(2023, 5, 2), ret_type=datetime)
        assert_equal(itr.get_next(), datetime(2023, 5, 3, 16, 0, 0))  # Wed May 3 2023
        assert_equal(itr.get_next(), datetime(2023, 5, 5, 16, 0, 0))  # Fri May 5 2023
        assert_equal(itr.get_next(), datetime(2023, 5, 6, 16, 0, 0))  # Sat May 6 2023
        assert_equal(itr.get_next(), datetime(2023, 5, 7, 16, 0, 0))  # Sun May 7 2023

        # INTERSECTION OF "every odd-numbered day" and "every Saturday"
        itr = croniter(
            expr,
            start_time=datetime(2023, 5, 2),
            ret_type=datetime,
            implement_cron_bug=True,
        )
        assert_equal(
            itr.get_next(), datetime(2023, 5, 13, 16, 0, 0)
        )  # Sat May  13 2023
        assert_equal(
            itr.get_next(), datetime(2023, 5, 27, 16, 0, 0)
        )  # Sat May  27 2023
        assert_equal(itr.get_next(), datetime(2023, 6, 3, 16, 0, 0))  # Sat June  3 2023
        assert_equal(
            itr.get_next(), datetime(2023, 6, 17, 16, 0, 0)
        )  # Sun June 17 2023

    def testMonth(self):
        base = datetime(2010, 1, 25)
        itr = croniter('0 0 1 * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.month, 2)
        assert_equal(n1.day, 1)
        n2 = itr.get_next(datetime)
        assert_equal(n2.month, 3)
        assert_equal(n2.day, 1)
        for i in range(8):
            itr.get_next()
        n3 = itr.get_next(datetime)
        assert_equal(n3.month, 12)
        assert_equal(n3.year, 2010)
        n4 = itr.get_next(datetime)
        assert_equal(n4.month, 1)
        assert_equal(n4.year, 2011)

    def testLastDayOfMonth(self):
        base = datetime(2015, 9, 4)
        itr = croniter('0 0 l * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.month, 9)
        assert_equal(n1.day, 30)
        n2 = itr.get_next(datetime)
        assert_equal(n2.month, 10)
        assert_equal(n2.day, 31)
        n3 = itr.get_next(datetime)
        assert_equal(n3.month, 11)
        assert_equal(n3.day, 30)
        n4 = itr.get_next(datetime)
        assert_equal(n4.month, 12)
        assert_equal(n4.day, 31)

    def testRangeWithUppercaseLastDayOfMonth(self):
        base = datetime(2015, 9, 4)
        itr = croniter('0 0 29-L * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.month, 9)
        assert_equal(n1.day, 29)
        n2 = itr.get_next(datetime)
        assert_equal(n2.month, 9)
        assert_equal(n2.day, 30)

    def testPrevLastDayOfMonth(self):
        base = datetime(2009, 12, 31, hour=20)
        itr = croniter('0 0 l * *', base)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 12)
        assert_equal(n1.day, 31)

        base = datetime(2009, 12, 31)
        itr = croniter('0 0 l * *', base)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 11)
        assert_equal(n1.day, 30)

        base = datetime(2010, 1, 5)
        itr = croniter('0 0 l * *', base)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 12)
        assert_equal(n1.day, 31)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 11)
        assert_equal(n1.day, 30)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 10)
        assert_equal(n1.day, 31)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 9)
        assert_equal(n1.day, 30)

        base = datetime(2010, 1, 31, minute=2)
        itr = croniter('* * l * *', base)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 1)
        assert_equal(n1.day, 31)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 1)
        assert_equal(n1.day, 31)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 12)
        assert_equal(n1.day, 31)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.month, 12)
        assert_equal(n1.day, 31)

    def testError(self):
        itr = croniter('* * * * *')
        assert_raises(TypeError, itr.get_next, str)
        assert_raises(ValueError, croniter, '* * * *')
        assert_raises(ValueError, croniter, '-90 * * * *')
        assert_raises(ValueError, croniter, 'a * * * *')
        assert_raises(ValueError, croniter, '* * * janu-jun *')
        assert_raises(ValueError, croniter, '1-1_0 * * * *')
        assert_raises(ValueError, croniter, '0-10/error * * * *')
        assert_raises(ValueError, croniter, '0-10/ * * * *')
        assert_raises(CroniterBadCronError, croniter, '0-1& * * * *', datetime.now())
        assert_raises(ValueError, croniter, '* * 5-100 * *')

    def testSundayToThursdayWithAlphaConversion(self):
        base = datetime(2010, 8, 25, 15, 56)  # wednesday
        itr = croniter('30 22 * * sun-thu', base)
        next = itr.get_next(datetime)

        assert_equal(base.year, next.year)
        assert_equal(base.month, next.month)
        assert_equal(base.day, next.day)
        assert_equal(22, next.hour)
        assert_equal(30, next.minute)

    def testOptimizeCronExpressions(self):
        """Non-optimal cron expressions that can be simplified."""
        wildcard = ['*']
        m, h, d, mon, dow, s = range(6)
        # Test each field individually
        assert_equal(croniter('0-59 0 1 1 0').expanded[m], wildcard)
        assert_equal(croniter('0 0-23 1 1 0').expanded[h], wildcard)
        assert_equal(croniter('0 0 1-31 1 0').expanded[dow], [0])
        assert_equal(croniter('0 0 1-31 1 *').expanded[d], wildcard)
        assert_equal(croniter('0 0 1 1-12 0').expanded[mon], wildcard)
        assert_equal(croniter('0 0 1 1 0-6').expanded[dow], [0, 1, 2, 3, 4, 5, 6])
        assert_equal(croniter('0 0 * 1 0-6').expanded[dow], wildcard)
        assert_equal(croniter('0 0 1 1 0-6').expanded[dow], [0, 1, 2, 3, 4, 5, 6])
        assert_equal(croniter('0 0 1 1 0-6,sat#3').expanded[dow], [0, 1, 2, 3, 4, 5, 6])
        assert_equal(croniter('0 0 * 1 0-6').expanded[dow], wildcard)
        assert_equal(croniter('0 0 * 1 0-6,sat#3').expanded[dow], wildcard)
        assert_equal(croniter('0 0 1 1 0 0-59').expanded[s], wildcard)
        # Real life examples
        assert_equal(croniter('30 1-12,0,10-23 15-21 * fri').expanded[h], wildcard)
        assert_equal(croniter('30 1-23,0 15-21 * fri').expanded[h], wildcard)

    def testBlockDupRanges(self):
        """Ensure that duplicate/overlapping ranges are squashed"""
        m, h, d, mon, dow, s = range(6)
        assert_equal(croniter('* 5,5,1-6 * * *').expanded[h], [1, 2, 3, 4, 5, 6])
        assert_equal(croniter('* * * * 2-3,4-5,3,3,3').expanded[dow], [2, 3, 4, 5])
        assert_equal(
            croniter('* * * * * 1,5,*/20,20,15').expanded[s], [0, 1, 5, 15, 20, 40]
        )
        assert_equal(croniter('* 4,1-4,5,4 * * *').expanded[h], [1, 2, 3, 4, 5])
        # Real life example
        assert_equal(
            croniter('59 23 * 1 wed,fri,mon-thu,tue,tue').expanded[dow], [1, 2, 3, 4, 5]
        )

    def testPrevMinute(self):
        base = datetime(2010, 8, 25, 15, 56)
        itr = croniter('*/1 * * * *', base)
        prev = itr.get_prev(datetime)
        assert_equal(base.year, prev.year)
        assert_equal(base.month, prev.month)
        assert_equal(base.day, prev.day)
        assert_equal(base.hour, prev.hour)
        assert_equal(base.minute, prev.minute + 1)

        base = datetime(2010, 8, 25, 15, 0)
        itr = croniter('*/1 * * * *', base)
        prev = itr.get_prev(datetime)
        assert_equal(base.year, prev.year)
        assert_equal(base.month, prev.month)
        assert_equal(base.day, prev.day)
        assert_equal(base.hour, prev.hour + 1)
        assert_equal(59, prev.minute)

        base = datetime(2010, 8, 25, 0, 0)
        itr = croniter('*/1 * * * *', base)
        prev = itr.get_prev(datetime)
        assert_equal(base.year, prev.year)
        assert_equal(base.month, prev.month)
        assert_equal(base.day, prev.day + 1)
        assert_equal(23, prev.hour)
        assert_equal(59, prev.minute)

    def testPrevDayOfMonthWithCrossing(self):
        """
        Test getting previous occurrence that crosses into previous month.
        """
        base = datetime(2012, 3, 15, 0, 0)
        itr = croniter('0 0 22 * *', base)
        prev = itr.get_prev(datetime)
        assert_equal(prev.year, 2012)
        assert_equal(prev.month, 2)
        assert_equal(prev.day, 22)
        assert_equal(prev.hour, 0)
        assert_equal(prev.minute, 0)

    def testPrevWeekDay(self):
        base = datetime(2010, 8, 25, 15, 56)
        itr = croniter('0 0 * * sat,sun', base)
        prev1 = itr.get_prev(datetime)
        assert_equal(prev1.year, base.year)
        assert_equal(prev1.month, base.month)
        assert_equal(prev1.day, 22)
        assert_equal(prev1.hour, 0)
        assert_equal(prev1.minute, 0)

        prev2 = itr.get_prev(datetime)
        assert_equal(prev2.year, base.year)
        assert_equal(prev2.month, base.month)
        assert_equal(prev2.day, 21)
        assert_equal(prev2.hour, 0)
        assert_equal(prev2.minute, 0)

        prev3 = itr.get_prev(datetime)
        assert_equal(prev3.year, base.year)
        assert_equal(prev3.month, base.month)
        assert_equal(prev3.day, 15)
        assert_equal(prev3.hour, 0)
        assert_equal(prev3.minute, 0)

    def testPrevNthWeekDay(self):
        base = datetime(2010, 8, 25, 15, 56)
        itr = croniter('0 0 * * sat#1,sun#2', base)
        prev1 = itr.get_prev(datetime)
        assert_equal(prev1.year, base.year)
        assert_equal(prev1.month, base.month)
        assert_equal(prev1.day, 8)
        assert_equal(prev1.hour, 0)
        assert_equal(prev1.minute, 0)

        prev2 = itr.get_prev(datetime)
        assert_equal(prev2.year, base.year)
        assert_equal(prev2.month, base.month)
        assert_equal(prev2.day, 7)
        assert_equal(prev2.hour, 0)
        assert_equal(prev2.minute, 0)

        prev3 = itr.get_prev(datetime)
        assert_equal(prev3.year, base.year)
        assert_equal(prev3.month, 7)
        assert_equal(prev3.day, 11)
        assert_equal(prev3.hour, 0)
        assert_equal(prev3.minute, 0)

    def testPrevWeekDay2(self):
        base = datetime(2010, 8, 25, 15, 56)
        itr = croniter('10 0 * * 0', base)
        prev = itr.get_prev(datetime)
        assert_equal(prev.day, 22)
        assert_equal(prev.hour, 0)
        assert_equal(prev.minute, 10)

    def testISOWeekday(self):
        base = datetime(2010, 2, 25)
        itr = croniter('0 0 * * 6', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.isoweekday(), 6)
        assert_equal(n1.day, 27)
        n2 = itr.get_next(datetime)
        assert_equal(n2.isoweekday(), 6)
        assert_equal(n2.day, 6)
        assert_equal(n2.month, 3)

    def testBug1(self):
        base = datetime(2012, 2, 24)
        itr = croniter('5 0 */2 * *', base)
        n1 = itr.get_prev(datetime)
        assert_equal(n1.hour, 0)
        assert_equal(n1.minute, 5)
        assert_equal(n1.month, 2)
        # month starts from 1, 3 .... then 21, 23
        # so correct is not 22  but 23
        assert_equal(n1.day, 23)

    def testBug2(self):
        base = datetime(2012, 1, 1, 0, 0)
        iter = croniter('0 * * 3 *', base)
        n1 = iter.get_next(datetime)
        assert_equal(n1.year, base.year)
        assert_equal(n1.month, 3)
        assert_equal(n1.day, base.day)
        assert_equal(n1.hour, base.hour)
        assert_equal(n1.minute, base.minute)

        n2 = iter.get_next(datetime)
        assert_equal(n2.year, base.year)
        assert_equal(n2.month, 3)
        assert_equal(n2.day, base.day)
        assert_equal(n2.hour, base.hour + 1)
        assert_equal(n2.minute, base.minute)

        n3 = iter.get_next(datetime)
        assert_equal(n3.year, base.year)
        assert_equal(n3.month, 3)
        assert_equal(n3.day, base.day)
        assert_equal(n3.hour, base.hour + 2)
        assert_equal(n3.minute, base.minute)

    def testBug3(self):
        base = datetime(2013, 3, 1, 12, 17, 34, 257877)
        c = croniter('00 03 16,30 * *', base)

        n1 = c.get_next(datetime)
        assert_equal(n1.month, 3)
        assert_equal(n1.day, 16)

        n2 = c.get_next(datetime)
        assert_equal(n2.month, 3)
        assert_equal(n2.day, 30)

        n3 = c.get_next(datetime)
        assert_equal(n3.month, 4)
        assert_equal(n3.day, 16)

        n4 = c.get_prev(datetime)
        assert_equal(n4.month, 3)
        assert_equal(n4.day, 30)

        n5 = c.get_prev(datetime)
        assert_equal(n5.month, 3)
        assert_equal(n5.day, 16)

        n6 = c.get_prev(datetime)
        assert_equal(n6.month, 2)
        assert_equal(n6.day, 16)

    def test_bug34(self):
        base = datetime(2012, 2, 24, 0, 0, 0)
        itr = croniter('* * 31 2 *', base)
        try:
            itr.get_next(datetime)
        except (CroniterBadDateError,) as ex:
            assert_equal(f'{ex}', 'failed to find next date')

    def testBug57(self):
        base = datetime(2012, 2, 24, 0, 0, 0)
        itr = croniter('0 4/6 * * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.hour, 4)
        assert_equal(n1.minute, 0)
        assert_equal(n1.month, 2)
        assert_equal(n1.day, 24)

        n1 = itr.get_prev(datetime)
        assert_equal(n1.hour, 22)
        assert_equal(n1.minute, 0)
        assert_equal(n1.month, 2)
        assert_equal(n1.day, 23)

        itr = croniter('0 0/6 * * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.hour, 6)
        assert_equal(n1.minute, 0)
        assert_equal(n1.month, 2)
        assert_equal(n1.day, 24)

        n1 = itr.get_prev(datetime)
        assert_equal(n1.hour, 0)
        assert_equal(n1.minute, 0)
        assert_equal(n1.month, 2)
        assert_equal(n1.day, 24)

    def test_multiple_months(self):
        base = datetime(2016, 3, 1, 0, 0, 0)
        itr = croniter('0 0 1 3,6,9,12 *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.hour, 0)
        assert_equal(n1.month, 6)
        assert_equal(n1.day, 1)
        assert_equal(n1.year, 2016)

        base = datetime(2016, 2, 15, 0, 0, 0)
        itr = croniter('0 0 1 3,6,9,12 *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.hour, 0)
        assert_equal(n1.month, 3)
        assert_equal(n1.day, 1)
        assert_equal(n1.year, 2016)

        base = datetime(2016, 12, 3, 10, 0, 0)
        itr = croniter('0 0 1 3,6,9,12 *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.hour, 0)
        assert_equal(n1.month, 3)
        assert_equal(n1.day, 1)
        assert_equal(n1.year, 2017)

        # The result with this parameters was incorrect.
        # assert_equal(p1.month, 12
        # AssertionError: 9 != 12
        base = datetime(2016, 3, 1, 0, 0, 0)
        itr = croniter('0 0 1 3,6,9,12 *', base)
        p1 = itr.get_prev(datetime)
        assert_equal(p1.hour, 0)
        assert_equal(p1.month, 12)
        assert_equal(p1.day, 1)
        assert_equal(p1.year, 2015)

        # check my change resolves another hidden bug.
        base = datetime(2016, 2, 1, 0, 0, 0)
        itr = croniter('0 0 1,15,31 * *', base)
        p1 = itr.get_prev(datetime)
        assert_equal(p1.hour, 0)
        assert_equal(p1.month, 1)
        assert_equal(p1.day, 31)
        assert_equal(p1.year, 2016)

        base = datetime(2016, 6, 1, 0, 0, 0)
        itr = croniter('0 0 1 3,6,9,12 *', base)
        p1 = itr.get_prev(datetime)
        assert_equal(p1.hour, 0)
        assert_equal(p1.month, 3)
        assert_equal(p1.day, 1)
        assert_equal(p1.year, 2016)

        base = datetime(2016, 3, 1, 0, 0, 0)
        itr = croniter('0 0 1 1,3,6,9,12 *', base)
        p1 = itr.get_prev(datetime)
        assert_equal(p1.hour, 0)
        assert_equal(p1.month, 1)
        assert_equal(p1.day, 1)
        assert_equal(p1.year, 2016)

        base = datetime(2016, 3, 1, 0, 0, 0)
        itr = croniter('0 0 1 1,3,6,9,12 *', base)
        p1 = itr.get_prev(datetime)
        assert_equal(p1.hour, 0)
        assert_equal(p1.month, 1)
        assert_equal(p1.day, 1)
        assert_equal(p1.year, 2016)

    def test_rangeGenerator(self):
        base = datetime(2013, 3, 4, 0, 0)
        itr = croniter('1-9/2 0 1 * *', base)
        n1 = itr.get_next(datetime)
        n2 = itr.get_next(datetime)
        n3 = itr.get_next(datetime)
        n4 = itr.get_next(datetime)
        n5 = itr.get_next(datetime)
        assert_equal(n1.minute, 1)
        assert_equal(n2.minute, 3)
        assert_equal(n3.minute, 5)
        assert_equal(n4.minute, 7)
        assert_equal(n5.minute, 9)

    def testPreviousHour(self):
        base = datetime(2012, 6, 23, 17, 41)
        itr = croniter('* 10 * * *', base)
        prev1 = itr.get_prev(datetime)
        assert_equal(prev1.year, base.year)
        assert_equal(prev1.month, base.month)
        assert_equal(prev1.day, base.day)
        assert_equal(prev1.hour, 10)
        assert_equal(prev1.minute, 59)

    def testPreviousDay(self):
        base = datetime(2012, 6, 27, 0, 15)
        itr = croniter('* * 26 * *', base)
        prev1 = itr.get_prev(datetime)
        assert_equal(prev1.year, base.year)
        assert_equal(prev1.month, base.month)
        assert_equal(prev1.day, 26)
        assert_equal(prev1.hour, 23)
        assert_equal(prev1.minute, 59)

    def testPreviousMonth(self):
        base = datetime(2012, 6, 18, 0, 15)
        itr = croniter('* * * 5 *', base)
        prev1 = itr.get_prev(datetime)
        assert_equal(prev1.year, base.year)
        assert_equal(prev1.month, 5)
        assert_equal(prev1.day, 31)
        assert_equal(prev1.hour, 23)
        assert_equal(prev1.minute, 59)

    def testPreviousDow(self):
        base = datetime(2012, 5, 13, 18, 48)
        itr = croniter('* * * * sat', base)
        prev1 = itr.get_prev(datetime)
        assert_equal(prev1.year, base.year)
        assert_equal(prev1.month, base.month)
        assert_equal(prev1.day, 12)
        assert_equal(prev1.hour, 23)
        assert_equal(prev1.minute, 59)

    def testGetCurrent(self):
        base = datetime(2012, 9, 25, 11, 24)
        itr = croniter('* * * * *', base)
        res = itr.get_current(datetime)
        assert_equal(base.year, res.year)
        assert_equal(base.month, res.month)
        assert_equal(base.day, res.day)
        assert_equal(base.hour, res.hour)
        assert_equal(base.minute, res.minute)

    def testTimezone(self):
        base = datetime(2013, 3, 4, 12, 15)
        itr = croniter('* * * * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.tzinfo, None)

        tokyo = pytz.timezone('Asia/Tokyo')
        itr2 = croniter('* * * * *', tokyo.localize(base))
        n2 = itr2.get_next(datetime)
        assert_equal(n2.tzinfo.zone, 'Asia/Tokyo')

    def testTimezoneDateutil(self):
        tokyo = dateutil.tz.gettz('Asia/Tokyo')
        base = datetime(2013, 3, 4, 12, 15, tzinfo=tokyo)
        itr = croniter('* * * * *', base)
        n1 = itr.get_next(datetime)
        assert_equal(n1.tzinfo.tzname(n1), 'JST')

    def testInitNoStartTime(self):
        itr = croniter('* * * * *')
        sleep(0.01)
        itr2 = croniter('* * * * *')
        # Greater does not exists in py26
        assert_true(itr2.cur > itr.cur)

    def assertScheduleTimezone(self, callback, expected_schedule):
        for expected_date, expected_offset in expected_schedule:
            d = callback()
            assert_equal(expected_date, d.replace(tzinfo=None))
            assert_equal(expected_offset, croniter._timedelta_to_seconds(d.utcoffset()))

    def testTimezoneWinterTime(self):
        tz = pytz.timezone('Europe/Athens')

        expected_schedule = [
            (datetime(2013, 10, 27, 2, 30, 0), 10800),
            (datetime(2013, 10, 27, 3, 0, 0), 10800),
            (datetime(2013, 10, 27, 3, 30, 0), 10800),
            (datetime(2013, 10, 27, 3, 0, 0), 7200),
            (datetime(2013, 10, 27, 3, 30, 0), 7200),
            (datetime(2013, 10, 27, 4, 0, 0), 7200),
            (datetime(2013, 10, 27, 4, 30, 0), 7200),
        ]

        start = datetime(2013, 10, 27, 2, 0, 0)
        ct = croniter('*/30 * * * *', tz.localize(start))
        self.assertScheduleTimezone(lambda: ct.get_next(datetime), expected_schedule)

        start = datetime(2013, 10, 27, 5, 0, 0)
        ct = croniter('*/30 * * * *', tz.localize(start))
        self.assertScheduleTimezone(
            lambda: ct.get_prev(datetime), reversed(expected_schedule)
        )

    def testTimezoneSummerTime(self):
        tz = pytz.timezone('Europe/Athens')

        expected_schedule = [
            (datetime(2013, 3, 31, 1, 30, 0), 7200),
            (datetime(2013, 3, 31, 2, 0, 0), 7200),
            (datetime(2013, 3, 31, 2, 30, 0), 7200),
            (datetime(2013, 3, 31, 4, 0, 0), 10800),
            (datetime(2013, 3, 31, 4, 30, 0), 10800),
        ]

        start = datetime(2013, 3, 31, 1, 0, 0)
        ct = croniter('*/30 * * * *', tz.localize(start))
        self.assertScheduleTimezone(lambda: ct.get_next(datetime), expected_schedule)

        start = datetime(2013, 3, 31, 5, 0, 0)
        ct = croniter('*/30 * * * *', tz.localize(start))
        self.assertScheduleTimezone(
            lambda: ct.get_prev(datetime), reversed(expected_schedule)
        )

    def test_std_dst(self):
        """
        DST tests

        This fixes https://github.com/taichino/croniter/issues/82

        """
        tz = pytz.timezone('Europe/Warsaw')
        # -> 2017-03-26 01:59+1:00 -> 03:00+2:00
        local_date = tz.localize(datetime(2017, 3, 26))
        val = croniter('0 0 * * *', local_date).get_next(datetime)
        assert_equal(val, tz.localize(datetime(2017, 3, 27)))
        #
        local_date = tz.localize(datetime(2017, 3, 26, 1))
        cr = croniter('0 * * * *', local_date)
        val = cr.get_next(datetime)
        assert_equal(val, tz.localize(datetime(2017, 3, 26, 3)))
        val = cr.get_current(datetime)
        assert_equal(val, tz.localize(datetime(2017, 3, 26, 3)))

        # -> 2017-10-29 02:59+2:00 -> 02:00+1:00
        local_date = tz.localize(datetime(2017, 10, 29))
        val = croniter('0 0 * * *', local_date).get_next(datetime)
        assert_equal(val, tz.localize(datetime(2017, 10, 30)))
        local_date = tz.localize(datetime(2017, 10, 29, 1, 59))
        val = croniter('0 * * * *', local_date).get_next(datetime)
        assert_equal(
            val.replace(tzinfo=None),
            tz.localize(datetime(2017, 10, 29, 2)).replace(tzinfo=None),
        )
        local_date = tz.localize(datetime(2017, 10, 29, 2))
        val = croniter('0 * * * *', local_date).get_next(datetime)
        assert_equal(val, tz.localize(datetime(2017, 10, 29, 3)))
        local_date = tz.localize(datetime(2017, 10, 29, 3))
        val = croniter('0 * * * *', local_date).get_next(datetime)
        assert_equal(val, tz.localize(datetime(2017, 10, 29, 4)))
        local_date = tz.localize(datetime(2017, 10, 29, 4))
        val = croniter('0 * * * *', local_date).get_next(datetime)
        assert_equal(val, tz.localize(datetime(2017, 10, 29, 5)))
        local_date = tz.localize(datetime(2017, 10, 29, 5))
        val = croniter('0 * * * *', local_date).get_next(datetime)
        assert_equal(val, tz.localize(datetime(2017, 10, 29, 6)))

    def test_std_dst2(self):
        """
        DST tests

        This fixes https://github.com/taichino/croniter/issues/87

        São Paulo, Brazil: 18/02/2018 00:00 -> 17/02/2018 23:00

        """
        tz = pytz.timezone('America/Sao_Paulo')
        local_dates = [
            # 17-22: 00 -> 18-00:00
            (tz.localize(datetime(2018, 2, 17, 21, 0, 0)), '2018-02-18 00:00:00-03:00'),
            # 17-23: 00 -> 18-00:00
            (tz.localize(datetime(2018, 2, 17, 22, 0, 0)), '2018-02-18 00:00:00-03:00'),
            # 17-23: 00 -> 18-00:00
            (tz.localize(datetime(2018, 2, 17, 23, 0, 0)), '2018-02-18 00:00:00-03:00'),
            # 18-00: 00 -> 19-00:00
            (tz.localize(datetime(2018, 2, 18, 0, 0, 0)), '2018-02-19 00:00:00-03:00'),
            # 17-22: 00 -> 18-00:00
            (tz.localize(datetime(2018, 2, 17, 21, 5, 0)), '2018-02-18 00:00:00-03:00'),
            # 17-23: 00 -> 18-00:00
            (tz.localize(datetime(2018, 2, 17, 22, 5, 0)), '2018-02-18 00:00:00-03:00'),
            # 17-23: 00 -> 18-00:00
            (tz.localize(datetime(2018, 2, 17, 23, 5, 0)), '2018-02-18 00:00:00-03:00'),
            # 18-00: 00 -> 19-00:00
            (tz.localize(datetime(2018, 2, 18, 0, 5, 0)), '2018-02-19 00:00:00-03:00'),
        ]
        ret1 = [croniter('0 0 * * *', d[0]).get_next(datetime) for d in local_dates]
        sret1 = [f'{d}' for d in ret1]
        lret1 = [f'{d[1]}' for d in local_dates]
        assert_equal(sret1, lret1)

    def test_std_dst3(self):
        """
        DST tests

        This fixes https://github.com/taichino/croniter/issues/90

        Adelaide, Australia: 15/04/2020 00:00 -> 15/03/2020

        """

        tz = pytz.timezone('Australia/Adelaide')

        schedule = croniter('0 0 24 * *', tz.localize(datetime(2020, 4, 15)))
        val1 = schedule.get_prev(datetime)
        dt1 = tz.localize(datetime(2020, 3, 24))
        assert_equal(val1, dt1)

        val2 = schedule.get_next(datetime)
        dt2 = tz.localize(datetime(2020, 4, 24))
        assert_equal(val2, dt2)

    def test_error_alpha_cron(self):
        assert_raises(CroniterNotAlphaError, croniter.expand, '* * * janu-jun *')

    def test_error_bad_cron(self):
        assert_raises(CroniterBadCronError, croniter.expand, '* * * *')
        assert_raises(
            CroniterBadCronError,
            croniter.expand,
            ('* ' * (max(VALID_LEN_EXPRESSION) + 1)).strip(),
        )

    def test_is_valid(self):
        assert_true(croniter.is_valid('0 * * * *'))
        assert_false(croniter.is_valid('0 * *'))
        assert_false(croniter.is_valid('* * * janu-jun *'))
        assert_true(croniter.is_valid('H 0 * * *', hash_id='abc'))

    def test_exactly_the_same_minute(self):
        base = datetime(2018, 3, 5, 12, 30, 50)
        itr = croniter('30 7,12,17 * * *', base)
        n1 = itr.get_prev(datetime)
        assert_equal(12, n1.hour)

        n2 = itr.get_prev(datetime)
        assert_equal(7, n2.hour)

        n3 = itr.get_next(datetime)
        assert_equal(12, n3.hour)

    def test_next_when_now_satisfies_cron(self):
        ts_a = datetime(2018, 5, 21, 0, 3, 0)
        ts_b = datetime(2018, 5, 21, 0, 4, 20)
        test_cron = '4 * * * *'

        next_a = croniter(test_cron, start_time=ts_a).get_next()
        next_b = croniter(test_cron, start_time=ts_b).get_next()

        assert_true(next_b > next_a)

    def test_milliseconds(self):
        """
        https://github.com/taichino/croniter/issues/107
        """

        _croniter = partial(croniter, '0 10 * * *', ret_type=datetime)

        dt = datetime(2018, 1, 2, 10, 0, 0, 500)
        assert_equal(
            _croniter(start_time=dt).get_prev(),
            datetime(2018, 1, 2, 10, 0),
        )
        assert_equal(
            _croniter(start_time=dt).get_next(),
            datetime(2018, 1, 3, 10, 0),
        )

        dt = datetime(2018, 1, 2, 10, 0, 1, 0)
        assert_equal(
            _croniter(start_time=dt).get_prev(),
            datetime(2018, 1, 2, 10, 0),
        )
        assert_equal(
            _croniter(start_time=dt).get_next(),
            datetime(2018, 1, 3, 10, 0),
        )

        dt = datetime(2018, 1, 2, 9, 59, 59, 999999)
        assert_equal(
            _croniter(start_time=dt).get_prev(),
            datetime(2018, 1, 1, 10, 0),
        )
        assert_equal(
            _croniter(start_time=dt).get_next(),
            datetime(2018, 1, 2, 10, 0),
        )

    def test_invalid_zerorepeat(self):
        assert_false(croniter.is_valid('*/0 * * * *'))

    def test_weekday_range(self):
        ret = []
        # jan 14 is monday
        dt = datetime(2019, 1, 14, 0, 0, 0, 0)
        for i in range(10):
            c = croniter('0 0 * * 2-4 *', start_time=dt)
            dt = datetime.fromtimestamp(c.get_next(), dateutil.tz.tzutc()).replace(
                tzinfo=None
            )
            ret.append(dt)
            dt += timedelta(days=1)
        sret = [f'{r}' for r in ret]
        assert_equal(
            sret,
            [
                '2019-01-15 00:00:00',
                '2019-01-16 00:00:01',
                '2019-01-17 00:00:02',
                '2019-01-22 00:00:00',
                '2019-01-23 00:00:01',
                '2019-01-24 00:00:02',
                '2019-01-29 00:00:00',
                '2019-01-30 00:00:01',
                '2019-01-31 00:00:02',
                '2019-02-05 00:00:00',
            ],
        )
        ret = []
        dt = datetime(2019, 1, 14, 0, 0, 0, 0)
        for i in range(10):
            c = croniter('0 0 * * 0-6 *', start_time=dt)
            dt = datetime.fromtimestamp(c.get_next(), dateutil.tz.tzutc()).replace(
                tzinfo=None
            )
            ret.append(dt)
            dt += timedelta(days=1)
        sret = [f'{r}' for r in ret]
        assert_equal(
            sret,
            [
                '2019-01-14 00:00:01',
                '2019-01-15 00:00:02',
                '2019-01-16 00:00:03',
                '2019-01-17 00:00:04',
                '2019-01-18 00:00:05',
                '2019-01-19 00:00:06',
                '2019-01-20 00:00:07',
                '2019-01-21 00:00:08',
                '2019-01-22 00:00:09',
                '2019-01-23 00:00:10',
            ],
        )

    def test_issue_monsun_117(self):
        ret = []
        dt = datetime(2019, 1, 14, 0, 0, 0, 0)
        for i in range(12):
            # c = croniter("0 0 * * Mon-Sun *", start_time=dt)
            c = croniter('0 0 * * Wed-Sun *', start_time=dt)
            dt = datetime.fromtimestamp(c.get_next(), tz=dateutil.tz.tzutc()).replace(
                tzinfo=None
            )
            ret.append(dt)
            dt += timedelta(days=1)
        sret = [f'{r}' for r in ret]
        assert_equal(
            sret,
            [
                '2019-01-16 00:00:00',
                '2019-01-17 00:00:01',
                '2019-01-18 00:00:02',
                '2019-01-19 00:00:03',
                '2019-01-20 00:00:04',
                '2019-01-23 00:00:00',
                '2019-01-24 00:00:01',
                '2019-01-25 00:00:02',
                '2019-01-26 00:00:03',
                '2019-01-27 00:00:04',
                '2019-01-30 00:00:00',
                '2019-01-31 00:00:01',
            ],
        )

    def test_mixdow(self):
        base = datetime(2018, 10, 1, 0, 0)
        itr = croniter('1 1 7,14,21,L * *', base)
        assert_true(isinstance(itr.get_next(), float))

    def test_match(self):
        assert_true(croniter.match('0 0 * * *', datetime(2019, 1, 14, 0, 0, 0, 0)))
        assert_false(croniter.match('0 0 * * *', datetime(2019, 1, 14, 0, 1, 0, 0)))
        assert_true(croniter.match('0 0 * * * 1', datetime(2023, 5, 25, 0, 0, 1, 0)))
        assert_false(croniter.match('0 0 * * * 1', datetime(2023, 5, 25, 0, 0, 2, 0)))
        assert_true(croniter.match('31 * * * *', datetime(2019, 1, 14, 1, 31, 0, 0)))
        assert_true(
            croniter.match(
                '0 0 10 * wed', datetime(2020, 6, 10, 0, 0, 0, 0), day_or=True
            )
        )
        assert_true(
            croniter.match(
                '0 0 10 * fri', datetime(2020, 6, 10, 0, 0, 0, 0), day_or=True
            )
        )
        assert_true(
            croniter.match(
                '0 0 10 * fri', datetime(2020, 6, 12, 0, 0, 0, 0), day_or=True
            )
        )
        assert_true(
            croniter.match(
                '0 0 10 * wed', datetime(2020, 6, 10, 0, 0, 0, 0), day_or=False
            )
        )
        assert_false(
            croniter.match(
                '0 0 10 * fri', datetime(2020, 6, 10, 0, 0, 0, 0), day_or=False
            )
        )
        assert_false(
            croniter.match(
                '0 0 10 * fri', datetime(2020, 6, 12, 0, 0, 0, 0), day_or=False
            )
        )

    def test_match_handle_bad_cron(self):
        # some cron expression can"t get prev value and should not raise exception
        assert_false(
            croniter.match('0 0 31 1 1#1', datetime(2020, 1, 31), day_or=False)
        )
        assert_false(
            croniter.match(
                '0 0 31 1 * 0 2024/2',
                datetime(2020, 1, 31),
            )
        )

    def test_match_range(self):
        assert_true(
            croniter.match_range(
                '0 0 * * *',
                datetime(2019, 1, 13, 0, 59, 0, 0),
                datetime(2019, 1, 14, 0, 1, 0, 0),
            )
        )
        assert_false(
            croniter.match_range(
                '0 0 * * *',
                datetime(2019, 1, 13, 0, 1, 0, 0),
                datetime(2019, 1, 13, 0, 59, 0, 0),
            )
        )
        assert_true(
            croniter.match_range(
                '0 0 * * * 1',
                datetime(2023, 5, 25, 0, 0, 0, 0),
                datetime(2023, 5, 25, 0, 0, 2, 0),
            )
        )
        assert_false(
            croniter.match_range(
                '0 0 * * * 1',
                datetime(2023, 5, 25, 0, 0, 2, 0),
                datetime(2023, 5, 25, 0, 0, 4, 0),
            )
        )
        assert_true(
            croniter.match_range(
                '0 0 * * * 1',
                datetime(2023, 5, 25, 0, 0, 1, 0),
                datetime(2023, 5, 25, 0, 0, 4, 0),
            )
        )
        assert_true(
            croniter.match_range(
                '31 * * * *',
                datetime(2019, 1, 14, 1, 30, 0, 0),
                datetime(2019, 1, 14, 1, 31, 0, 0),
            )
        )
        assert_true(
            croniter.match_range(
                '0 0 10 * wed',
                datetime(2020, 6, 9, 0, 0, 0, 0),
                datetime(2020, 6, 11, 0, 0, 0, 0),
                day_or=True,
            )
        )
        assert_true(
            croniter.match_range(
                '0 0 10 * fri',
                datetime(2020, 6, 10, 0, 0, 0, 0),
                datetime(2020, 6, 11, 0, 0, 0, 0),
                day_or=True,
            )
        )
        assert_true(
            croniter.match_range(
                '0 0 10 * fri',
                datetime(2020, 6, 11, 0, 0, 0, 0),
                datetime(2020, 6, 12, 0, 0, 0, 0),
                day_or=True,
            )
        )
        assert_true(
            croniter.match_range(
                '0 0 10 * wed',
                datetime(2020, 6, 9, 0, 0, 0, 0),
                datetime(2020, 6, 12, 0, 0, 0, 0),
                day_or=False,
            )
        )
        assert_false(
            croniter.match_range(
                '0 0 10 * fri',
                datetime(2020, 6, 8, 0, 0, 0, 0),
                datetime(2020, 6, 9, 0, 0, 0, 0),
                day_or=False,
            )
        )
        assert_false(
            croniter.match_range(
                '0 0 10 * fri',
                datetime(2020, 6, 7, 0, 0, 0, 0),
                datetime(2020, 6, 11, 0, 0, 0, 0),
                day_or=False,
            )
        )
        assert_false(
            croniter.match_range(
                '2 4 1 * wed',
                datetime(2019, 1, 1, 3, 2, 0, 0),
                datetime(2019, 1, 1, 5, 2, 0, 0),
                day_or=False,
            )
        )

    def test_dst_issue90_st31ny(self):
        tz = pytz.timezone('Europe/Paris')
        now = datetime(2020, 3, 29, 1, 59, 55, tzinfo=tz)
        it = croniter('1 2 * * *', now)
        #
        # Taking around DST @ 29/03/20 01:59
        #
        ret = [
            it.get_next(datetime).isoformat(),
            it.get_prev(datetime).isoformat(),
            it.get_prev(datetime).isoformat(),
            it.get_next(datetime).isoformat(),
            it.get_next(datetime).isoformat(),
        ]
        assert_equal(
            ret,
            [
                '2020-03-30T02:01:00+02:00',
                '2020-03-29T01:01:00+01:00',
                '2020-03-28T03:01:00+01:00',
                '2020-03-29T03:01:00+02:00',
                '2020-03-30T02:01:00+02:00',
            ],
        )
        #
        nowp = datetime(2020, 3, 28, 1, 58, 55, tzinfo=tz)
        itp = croniter('1 2 * * *', nowp)
        retp = [
            itp.get_next(datetime).isoformat(),
            itp.get_prev(datetime).isoformat(),
            itp.get_prev(datetime).isoformat(),
            itp.get_next(datetime).isoformat(),
            itp.get_next(datetime).isoformat(),
        ]
        assert_equal(
            retp,
            [
                '2020-03-29T03:01:00+02:00',
                '2020-03-29T01:01:00+01:00',
                '2020-03-28T03:01:00+01:00',
                '2020-03-29T03:01:00+02:00',
                '2020-03-30T02:01:00+02:00',
            ],
        )
        #
        nowt = datetime(2020, 3, 29, 2, 0, 0, tzinfo=tz)
        itt = croniter('1 2 * * *', nowt)
        rett = [
            itt.get_next(datetime).isoformat(),
            itt.get_prev(datetime).isoformat(),
            itt.get_prev(datetime).isoformat(),
            itt.get_next(datetime).isoformat(),
            itt.get_next(datetime).isoformat(),
        ]
        assert_equal(
            rett,
            [
                '2020-03-30T02:01:00+02:00',
                '2020-03-29T01:01:00+01:00',
                '2020-03-28T03:01:00+01:00',
                '2020-03-29T03:01:00+02:00',
                '2020-03-30T02:01:00+02:00',
            ],
        )

    def test_dst_iter(self):
        tz = pytz.timezone('Asia/Hebron')
        now = datetime(2022, 3, 26, 0, 0, 0, tzinfo=tz)
        it = croniter('0 0 * * *', now)
        ret = [
            it.get_next(datetime).isoformat(),
            it.get_next(datetime).isoformat(),
            it.get_next(datetime).isoformat(),
        ]
        assert_equal(
            ret,
            [
                '2022-03-26T00:00:00+02:00',
                '2022-03-27T01:00:00+03:00',
                '2022-03-28T00:00:00+03:00',
            ],
        )

    def test_nth_wday_simple(self):
        f = lambda y, m, w: croniter._get_nth_weekday_of_month(y, m, w)
        sun, mon, tue, wed, thu, fri, sat = range(7)

        assert_equal(f(2000, 1, mon), (3, 10, 17, 24, 31))
        assert_equal(f(2000, 2, tue), (1, 8, 15, 22, 29))  # Leap year
        assert_equal(f(2000, 3, wed), (1, 8, 15, 22, 29))
        assert_equal(f(2000, 4, thu), (6, 13, 20, 27))
        assert_equal(f(2000, 2, fri), (4, 11, 18, 25))
        assert_equal(f(2000, 2, sat), (5, 12, 19, 26))

    def test_nth_as_last_wday_simple(self):
        f = lambda y, m, w: croniter._get_nth_weekday_of_month(y, m, w)[-1]
        sun, mon, tue, wed, thu, fri, sat = range(7)
        assert_equal(f(2000, 2, tue), 29)
        assert_equal(f(2000, 2, sun), 27)
        assert_equal(f(2000, 2, mon), 28)
        assert_equal(f(2000, 2, wed), 23)
        assert_equal(f(2000, 2, thu), 24)
        assert_equal(f(2000, 2, fri), 25)
        assert_equal(f(2000, 2, sat), 26)

    def test_wdom_core_leap_year(self):
        f = lambda y, m, w: croniter._get_nth_weekday_of_month(y, m, w)[-1]
        sun, mon, tue, wed, thu, fri, sat = range(7)
        assert_equal(f(2000, 2, tue), 29)
        assert_equal(f(2000, 2, sun), 27)
        assert_equal(f(2000, 2, mon), 28)
        assert_equal(f(2000, 2, wed), 23)
        assert_equal(f(2000, 2, thu), 24)
        assert_equal(f(2000, 2, fri), 25)
        assert_equal(f(2000, 2, sat), 26)

    def test_lwom_friday(self):
        it = croniter('0 0 * * L5', datetime(1987, 1, 15), ret_type=datetime)
        items = [next(it) for i in range(12)]
        assert_equal(
            items,
            [
                datetime(1987, 1, 30),
                datetime(1987, 2, 27),
                datetime(1987, 3, 27),
                datetime(1987, 4, 24),
                datetime(1987, 5, 29),
                datetime(1987, 6, 26),
                datetime(1987, 7, 31),
                datetime(1987, 8, 28),
                datetime(1987, 9, 25),
                datetime(1987, 10, 30),
                datetime(1987, 11, 27),
                datetime(1987, 12, 25),
            ],
        )

    def test_lwom_friday_2hours(self):
        # This works with +/- "days=1' in proc_day_of_week_last() and I don't know WHY?!?
        it = croniter('0 1,5 * * L5', datetime(1987, 1, 15), ret_type=datetime)
        items = [next(it) for i in range(12)]
        assert_equal(
            items,
            [
                datetime(1987, 1, 30, 1),
                datetime(1987, 1, 30, 5),
                datetime(1987, 2, 27, 1),
                datetime(1987, 2, 27, 5),
                datetime(1987, 3, 27, 1),
                datetime(1987, 3, 27, 5),
                datetime(1987, 4, 24, 1),
                datetime(1987, 4, 24, 5),
                datetime(1987, 5, 29, 1),
                datetime(1987, 5, 29, 5),
                datetime(1987, 6, 26, 1),
                datetime(1987, 6, 26, 5),
            ],
        )

    def test_lwom_friday_2xh_2xm(self):
        it = croniter('0,30 1,5 * * L5', datetime(1987, 1, 15), ret_type=datetime)
        items = [next(it) for i in range(12)]
        assert_equal(
            items,
            [
                datetime(1987, 1, 30, 1, 0),
                datetime(1987, 1, 30, 1, 30),
                datetime(1987, 1, 30, 5, 0),
                datetime(1987, 1, 30, 5, 30),
                datetime(1987, 2, 27, 1, 0),
                datetime(1987, 2, 27, 1, 30),
                datetime(1987, 2, 27, 5, 0),
                datetime(1987, 2, 27, 5, 30),
                datetime(1987, 3, 27, 1, 0),
                datetime(1987, 3, 27, 1, 30),
                datetime(1987, 3, 27, 5, 0),
                datetime(1987, 3, 27, 5, 30),
            ],
        )

    def test_lwom_saturday_rev(self):
        it = croniter(
            '0 0 * * L6', datetime(2017, 12, 31), ret_type=datetime, is_prev=True
        )
        items = [next(it) for i in range(12)]
        assert_equal(
            items,
            [
                datetime(2017, 12, 30),
                datetime(2017, 11, 25),
                datetime(2017, 10, 28),
                datetime(2017, 9, 30),
                datetime(2017, 8, 26),
                datetime(2017, 7, 29),
                datetime(2017, 6, 24),
                datetime(2017, 5, 27),
                datetime(2017, 4, 29),
                datetime(2017, 3, 25),
                datetime(2017, 2, 25),
                datetime(2017, 1, 28),
            ],
        )

    def test_lwom_tue_thu(self):
        it = croniter('0 0 * * L2,L4', datetime(2016, 6, 1), ret_type=datetime)
        items = [next(it) for i in range(10)]
        assert_equal(
            items,
            [
                datetime(2016, 6, 28),
                datetime(2016, 6, 30),
                datetime(2016, 7, 26),
                datetime(2016, 7, 28),
                datetime(2016, 8, 25),  # last tuesday comes before the last thursday
                datetime(2016, 8, 30),
                datetime(2016, 9, 27),
                datetime(2016, 9, 29),
                datetime(2016, 10, 25),
                datetime(2016, 10, 27),
            ],
        )

    def test_hash_mixup_all_fri_3rd_sat(self):
        # It appears that it's not possible to MIX a literal dow with a `dow#n` format
        cron_a = '0 0 * * 6#3'
        cron_b = '0 0 * * 5'
        cron_c = '0 0 * * 5,6#3'
        start = datetime(2021, 3, 1)
        expect_a = [datetime(2021, 3, 20)]
        expect_b = [
            datetime(2021, 3, 5),
            datetime(2021, 3, 12),
            datetime(2021, 3, 19),
            datetime(2021, 3, 26),
        ]
        expect_c = sorted(set(expect_a) & set(expect_b))

        def getn(expr, n):
            it = croniter(expr, start, ret_type=datetime)
            return [next(it) for i in range(n)]

        assert_equal(getn(cron_a, 1), expect_a)
        assert_equal(getn(cron_b, 4), expect_b)
        with pytest.raises(CroniterUnsupportedSyntaxError):
            assert_equal(getn(cron_c, 5), expect_c)

    def test_lwom_mixup_all_fri_last_sat(self):
        # Based on the failure of test_hash_mixup_all_fri_3rd_sat, we should expect this to fail too as this implementation simply extends nth_weekday_of_month
        cron_a = '0 0 * * L6'
        cron_b = '0 0 * * 5'
        cron_c = '0 0 * * 5,L6'
        start = datetime(2021, 3, 1)
        expect_a = [datetime(2021, 3, 27)]
        expect_b = [
            datetime(2021, 3, 5),
            datetime(2021, 3, 12),
            datetime(2021, 3, 19),
            datetime(2021, 3, 26),
        ]
        expect_c = sorted(set(expect_a) | set(expect_b))

        def getn(expr, n):
            it = croniter(expr, start, ret_type=datetime)
            return [next(it) for i in range(n)]

        assert_equal(getn(cron_a, 1), expect_a)
        assert_equal(getn(cron_b, 4), expect_b)
        with pytest.raises(CroniterUnsupportedSyntaxError):
            assert_equal(getn(cron_c, 5), expect_c)

    def test_lwom_mixup_firstlast_sat(self):
        # First saturday, last saturday
        start = datetime(2021, 3, 1)
        cron_a = '0 0 * * 6#1'
        cron_b = '0 0 * * L6'
        cron_c = '0 0 * * L6,6#1'
        expect_a = [
            datetime(2021, 3, 6),
            datetime(2021, 4, 3),
            datetime(2021, 5, 1),
        ]
        expect_b = [
            datetime(2021, 3, 27),
            datetime(2021, 4, 24),
            datetime(2021, 5, 29),
        ]
        expect_c = sorted(expect_a + expect_b)

        def getn(expr, n):
            it = croniter(expr, start, ret_type=datetime)
            return [next(it) for i in range(n)]

        assert_equal(getn(cron_a, 3), expect_a)
        assert_equal(getn(cron_b, 3), expect_b)
        assert_equal(getn(cron_c, 6), expect_c)

    def test_lwom_mixup_4th_and_last(self):
        # 4th and last monday
        start = datetime(2021, 11, 1)
        cron_a = '0 0 * * 1#4'
        cron_b = '0 0 * * L1'
        cron_c = '0 0 * * 1#4,L1'
        expect_a = [
            datetime(2021, 11, 22),
            datetime(2021, 12, 27),
            datetime(2022, 1, 24),
        ]
        expect_b = [
            datetime(2021, 11, 29),
            datetime(2021, 12, 27),
            datetime(2022, 1, 31),
        ]
        expect_c = sorted(set(expect_a) | set(expect_b))

        def getn(expr, n):
            it = croniter(expr, start, ret_type=datetime)
            return [next(it) for i in range(n)]

        assert_equal(getn(cron_a, 3), expect_a)
        assert_equal(getn(cron_b, 3), expect_b)
        assert_equal(getn(cron_c, 5), expect_c)

    def test_configure_second_location(self):
        base = datetime(2010, 8, 25, 0)
        itr = croniter('59 58 1 * * *', base, second_at_beginning=True)
        n = itr.get_next(datetime)
        assert_equal(n.year, base.year)
        assert_equal(n.month, base.month)
        assert_equal(n.day, base.day)
        assert_equal(n.hour, 1)
        assert_equal(n.minute, 58)
        assert_equal(n.second, 59)

    def test_nth_out_of_range(self):
        with pytest.raises(CroniterBadCronError):
            croniter('0 0 * * 1#7')
        with pytest.raises(CroniterBadCronError):
            croniter('0 0 * * 1#0')

    def test_last_out_of_range(self):
        with pytest.raises(CroniterBadCronError):
            croniter('0 0 * * L-1')
        with pytest.raises(CroniterBadCronError):
            croniter('0 0 * * L8')

    def test_question_mark(self):
        base = datetime(2010, 8, 25, 15, 56)
        itr = croniter('0 0 1 * ?', base)
        n = itr.get_next(datetime)
        assert_equal(n.year, base.year)
        assert_equal(n.month, 9)
        assert_equal(n.day, 1)
        assert_equal(n.hour, 0)
        assert_equal(n.minute, 0)

    def test_invalid_question_mark(self):
        assert_raises(CroniterBadCronError, croniter, '? * * * *')
        assert_raises(CroniterBadCronError, croniter, '* ? * * *')
        assert_raises(CroniterBadCronError, croniter, '* * ?,* * *')

    def test_year(self):
        itr1 = croniter('0 0 11 * * 0 2060', datetime(2050, 1, 1))
        n1 = itr1.get_next(datetime)
        assert_equal(n1.year, 2060)
        assert_equal(n1.month, 1)
        assert_equal(n1.day, 11)
        n2 = itr1.get_next(datetime)
        assert_equal(n2.year, 2060)
        assert_equal(n2.month, 2)
        assert_equal(n2.day, 11)

        itr2 = croniter('0 0 11 * * 0 2050-2060', datetime(2055, 1, 30))
        n3 = itr2.get_next(datetime)
        assert_equal(n3.year, 2055)
        assert_equal(n3.month, 2)
        assert_equal(n3.day, 11)

        itr3 = croniter('0 0 29 2 * 0 2025,2021-2023,2028', datetime(2020, 1, 1))
        n4 = itr3.get_next(datetime)
        assert_equal(n4.year, 2028)
        assert_equal(n4.month, 2)
        assert_equal(n4.day, 29)

        itr4 = croniter('0 0 29 2 * 0 2025,*', datetime(2020, 1, 1))
        n5 = itr4.get_next(datetime)
        assert_equal(n5.year, 2020)
        assert_equal(n5.month, 2)
        assert_equal(n5.day, 29)

        itr5 = croniter('0 0 29 2 * 0 2022/3', datetime(2020, 1, 1))
        n6 = itr5.get_next(datetime)
        assert_equal(n6.year, 2028)
        assert_equal(n6.month, 2)
        assert_equal(n6.day, 29)

        itr6 = croniter('0 0 29 2 * 0 2023-2035/3', datetime(2020, 1, 1))
        n7 = itr6.get_next(datetime)
        assert_equal(n7.year, 2032)
        assert_equal(n7.month, 2)
        assert_equal(n7.day, 29)

    def test_year_with_other_field(self):
        itr1 = croniter('0 0 31 11-12 * 0 2023', datetime(2000, 1, 30))
        n1 = itr1.get_next(datetime)
        assert_equal(n1.year, 2023)
        assert_equal(n1.month, 12)
        assert_equal(n1.day, 31)

        itr2 = croniter('0 0 31 1-2 * 0 2023-2025', datetime(2024, 12, 30))
        n2 = itr2.get_next(datetime)
        assert_equal(n2.year, 2025)
        assert_equal(n2.month, 1)
        assert_equal(n2.day, 31)

        itr3 = croniter('0 0 1 1 1 0 2020-2030', datetime(2000, 1, 1), day_or=False)
        n3 = itr3.get_next(datetime)
        assert_equal(n3.year, 2024)
        assert_equal(n3.month, 1)
        assert_equal(n3.day, 1)

    def test_year_get_prev(self):
        itr1 = croniter('0 0 11 * * 0 2000', datetime(2010, 1, 1))
        p1 = itr1.get_prev(datetime)
        assert_equal(p1.year, 2000)
        assert_equal(p1.month, 12)
        assert_equal(p1.day, 11)

        itr2 = croniter('0 0 11 * * 0 2000', datetime(2010, 1, 1))
        p2 = itr2.get_prev(datetime)
        assert_equal(p2.year, 2000)
        assert_equal(p2.month, 12)
        assert_equal(p2.day, 11)

        itr2 = croniter('0 0 29 2 * 0 2010-2030', datetime(2020, 1, 1))
        p2 = itr2.get_prev(datetime)
        assert_equal(p2.year, 2016)
        assert_equal(p2.month, 2)
        assert_equal(p2.day, 29)

    def test_year_match(self):
        assert_true(croniter.match('* * * * * * 2024', datetime(2024, 1, 1)))
        assert_true(
            croniter.match(
                '59 58 23 31 12 * 2024',
                datetime(2024, 12, 31, 23, 58, 59),
                second_at_beginning=True,
            )
        )
        assert_false(croniter.match('* * * * * * 2024-2026', datetime(2027, 1, 1)))
        assert_false(croniter.match('* * * * * * 2024/2', datetime(2025, 1, 1)))

    def test_year_bad_date_error(self):
        with pytest.raises(CroniterBadDateError):
            itr = croniter('* * * * * * 2020', datetime(2030, 1, 1))
            itr.get_next()
        with pytest.raises(CroniterBadDateError):
            itr = croniter('* * * * * * 2020', datetime(2000, 1, 1))
            itr.get_prev()
        with pytest.raises(CroniterBadDateError):
            itr = croniter('* * 29 2 * * 2021-2023', datetime(2000, 1, 1))
            itr.get_next()

    def test_year_with_second_at_beginning(self):
        base = datetime(2050, 1, 1)
        itr = croniter('59 58 23 31 12 * 2070', base, second_at_beginning=True)
        n = itr.get_next(datetime)
        assert_equal(n.year, 2070)
        assert_equal(n.month, 12)
        assert_equal(n.day, 31)
        assert_equal(n.hour, 23)
        assert_equal(n.minute, 58)
        assert_equal(n.second, 59)

    def test_invalid_year(self):
        assert_raises(CroniterBadCronError, croniter, '0 0 1 * * 0 1000')
        assert_raises(CroniterBadCronError, croniter, '0 0 1 * * 0 99999')
        assert_raises(CroniterBadCronError, croniter, '0 0 1 * * 0 2070#3')

    def test_issue_47(self):
        base = datetime(2021, 3, 30, 4, 0)
        itr = croniter('0 6 30 3 *', base)
        prev1 = itr.get_prev(datetime)
        assert_equal(prev1.year, base.year - 1)
        assert_equal(prev1.month, 3)
        assert_equal(prev1.day, 30)
        assert_equal(prev1.hour, 6)
        assert_equal(prev1.minute, 0)

    maxDiff = None

    def test_issue_142_dow(self):
        ret = []
        for i in range(1, 31):
            ret.append(
                (
                    i,
                    croniter(
                        '35 * 1-l/8 * *', datetime(2020, 1, i), ret_type=datetime
                    ).get_next(),
                )
            )
            i += 1
        assert_equal(
            ret,
            [
                (1, datetime(2020, 1, 1, 0, 35)),
                (2, datetime(2020, 1, 9, 0, 35)),
                (3, datetime(2020, 1, 9, 0, 35)),
                (4, datetime(2020, 1, 9, 0, 35)),
                (5, datetime(2020, 1, 9, 0, 35)),
                (6, datetime(2020, 1, 9, 0, 35)),
                (7, datetime(2020, 1, 9, 0, 35)),
                (8, datetime(2020, 1, 9, 0, 35)),
                (9, datetime(2020, 1, 9, 0, 35)),
                (10, datetime(2020, 1, 17, 0, 35)),
                (11, datetime(2020, 1, 17, 0, 35)),
                (12, datetime(2020, 1, 17, 0, 35)),
                (13, datetime(2020, 1, 17, 0, 35)),
                (14, datetime(2020, 1, 17, 0, 35)),
                (15, datetime(2020, 1, 17, 0, 35)),
                (16, datetime(2020, 1, 17, 0, 35)),
                (17, datetime(2020, 1, 17, 0, 35)),
                (18, datetime(2020, 1, 25, 0, 35)),
                (19, datetime(2020, 1, 25, 0, 35)),
                (20, datetime(2020, 1, 25, 0, 35)),
                (21, datetime(2020, 1, 25, 0, 35)),
                (22, datetime(2020, 1, 25, 0, 35)),
                (23, datetime(2020, 1, 25, 0, 35)),
                (24, datetime(2020, 1, 25, 0, 35)),
                (25, datetime(2020, 1, 25, 0, 35)),
                (26, datetime(2020, 2, 1, 0, 35)),
                (27, datetime(2020, 2, 1, 0, 35)),
                (28, datetime(2020, 2, 1, 0, 35)),
                (29, datetime(2020, 2, 1, 0, 35)),
                (30, datetime(2020, 2, 1, 0, 35)),
            ],
        )

    def test_issue145_getnext(self):
        # Example of quarterly event cron schedule
        start = datetime(2020, 9, 24)
        cron = '0 13 8 1,4,7,10 wed'
        with pytest.raises(CroniterBadDateError):
            it = croniter(cron, start, day_or=False, max_years_between_matches=1)
            it.get_next()
        # New functionality (0.3.35) allowing croniter to find spare matches of cron patterns across multiple years
        it = croniter(cron, start, day_or=False, max_years_between_matches=5)
        assert_equal(it.get_next(datetime), datetime(2025, 1, 8, 13))

    def test_explicit_year_forward(self):
        start = datetime(2020, 9, 24)
        cron = '0 13 8 1,4,7,10 wed'

        # Expect exception because no explicit range was provided.  Therefore, the caller should be made aware that an implicit limit was hit.
        ccron = croniter(cron, start, day_or=False)
        ccron._max_years_between_matches = 1
        iterable = ccron.all_next()
        with pytest.raises(CroniterBadDateError):
            next(iterable)

        iterable = croniter(
            cron, start, day_or=False, max_years_between_matches=5
        ).all_next(datetime)
        n = next(iterable)
        assert_equal(n, datetime(2025, 1, 8, 13))

        # If the explicitly given lookahead isn't enough to reach the next date, that's fine.  The caller specified the maximum gap, so no just stop iteration
        iterable = croniter(
            cron, start, day_or=False, max_years_between_matches=2
        ).all_next(datetime)
        with pytest.raises(StopIteration):
            next(iterable)

    def test_issue151(self):
        """."""
        assert_true(
            croniter.match('* * * * *', datetime(2019, 1, 14, 11, 0, 59, 999999))
        )

    def test_overflow(self):
        """."""
        assert_raises(
            CroniterBadCronError, croniter, '0-10000000 * * * *', datetime.now()
        )

    def test_issue156(self):
        """."""
        dt = croniter(
            '* * * * *,0', datetime(2019, 1, 14, 11, 0, 59, 999999)
        ).get_next()
        assert_equal(1547463660.0, dt)
        assert_raises(CroniterBadCronError, croniter, '* * * * *,b')
        dt = croniter(
            '0 0 * * *,sat#3', datetime(2019, 1, 14, 11, 0, 59, 999999)
        ).get_next()
        assert_equal(1547856000.0, dt)

    def test_confirm_sort(self):
        m, h, d, mon, dow, s = range(6)
        assert_equal(croniter('0 8,22,10,23 1 1 0').expanded[h], [8, 10, 22, 23])
        assert_equal(croniter('0 0 25-L 1 0').expanded[d], [25, 26, 27, 28, 29, 30, 31])
        assert_equal(croniter('1 1 7,14,21,L * *').expanded[d], [7, 14, 21, 'l'])
        assert_equal(croniter('0 0 * * *,sat#3').expanded[dow], ['*', 6])

    def test_issue_k6(self):
        assert_raises(CroniterBadCronError, croniter, '0 0 0 0 0')
        assert_raises(CroniterBadCronError, croniter, '0 0 0 1 0')

    def test_issue_k11(self):
        now = pytz.timezone('America/New_York').localize(
            datetime(2019, 1, 14, 11, 0, 59)
        )
        nextnow = croniter('* * * * * ').next(datetime, start_time=now)
        nextnow2 = croniter('* * * * * ', now).next(datetime)
        for nt in nextnow, nextnow2:
            assert_equal(nt.tzinfo.zone, 'America/New_York')
            assert_equal(int(croniter._datetime_to_timestamp(nt)), 1547481660)

    def test_issue_k12(self):
        tz = pytz.timezone('Europe/Athens')
        base = datetime(2010, 1, 23, 12, 18, tzinfo=tz)
        itr = croniter('* * * * *')
        itr.set_current(start_time=base)
        n1 = itr.get_next()  # 19

        assert_equal(n1, datetime_to_timestamp(base) + 60)

    def test_issue_k34(self):
        # invalid cron, but should throw appropriate exception
        assert_raises(CroniterBadCronError, croniter, '4 0 L/2 2 0')

    def test_issue_k33(self):
        y = 2018
        # At 11:30 PM, between day 1 and 7 of the month, Monday through Friday, only in January
        ret = []
        for i in range(10):
            cron = croniter(
                '30 23 1-7 JAN MON-FRI#1', datetime(y + i, 1, 1), ret_type=datetime
            )
            for j in range(7):
                d = cron.get_next()
                if d.year == y + i:
                    ret.append(d)
        rets = [
            datetime(2018, 1, 1, 23, 30),
            datetime(2018, 1, 2, 23, 30),
            datetime(2018, 1, 3, 23, 30),
            datetime(2018, 1, 4, 23, 30),
            datetime(2018, 1, 5, 23, 30),
            datetime(2019, 1, 1, 23, 30),
            datetime(2019, 1, 2, 23, 30),
            datetime(2019, 1, 3, 23, 30),
            datetime(2019, 1, 4, 23, 30),
            datetime(2019, 1, 7, 23, 30),
            datetime(2020, 1, 1, 23, 30),
            datetime(2020, 1, 2, 23, 30),
            datetime(2020, 1, 3, 23, 30),
            datetime(2020, 1, 6, 23, 30),
            datetime(2020, 1, 7, 23, 30),
            datetime(2021, 1, 1, 23, 30),
            datetime(2021, 1, 4, 23, 30),
            datetime(2021, 1, 5, 23, 30),
            datetime(2021, 1, 6, 23, 30),
            datetime(2021, 1, 7, 23, 30),
            datetime(2022, 1, 3, 23, 30),
            datetime(2022, 1, 4, 23, 30),
            datetime(2022, 1, 5, 23, 30),
            datetime(2022, 1, 6, 23, 30),
            datetime(2022, 1, 7, 23, 30),
            datetime(2023, 1, 2, 23, 30),
            datetime(2023, 1, 3, 23, 30),
            datetime(2023, 1, 4, 23, 30),
            datetime(2023, 1, 5, 23, 30),
            datetime(2023, 1, 6, 23, 30),
            datetime(2024, 1, 1, 23, 30),
            datetime(2024, 1, 2, 23, 30),
            datetime(2024, 1, 3, 23, 30),
            datetime(2024, 1, 4, 23, 30),
            datetime(2024, 1, 5, 23, 30),
            datetime(2025, 1, 1, 23, 30),
            datetime(2025, 1, 2, 23, 30),
            datetime(2025, 1, 3, 23, 30),
            datetime(2025, 1, 6, 23, 30),
            datetime(2025, 1, 7, 23, 30),
            datetime(2026, 1, 1, 23, 30),
            datetime(2026, 1, 2, 23, 30),
            datetime(2026, 1, 5, 23, 30),
            datetime(2026, 1, 6, 23, 30),
            datetime(2026, 1, 7, 23, 30),
            datetime(2027, 1, 1, 23, 30),
            datetime(2027, 1, 4, 23, 30),
            datetime(2027, 1, 5, 23, 30),
            datetime(2027, 1, 6, 23, 30),
            datetime(2027, 1, 7, 23, 30),
        ]
        assert_equal(ret, rets)
        croniter.expand('30 6 1-7 MAY MON#1')

    def test_bug_62_leap(self):
        ret = croniter('15 22 29 2 *', datetime(2024, 2, 29)).get_prev(datetime)
        assert_equal(ret, datetime(2020, 2, 29, 22, 15))

    def test_expand_from_start_time_minute(self):
        seven_seconds_interval_pattern = '*/7 * * * *'
        ret1 = croniter(
            seven_seconds_interval_pattern,
            start_time=datetime(2024, 7, 11, 10, 11),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret1, datetime(2024, 7, 11, 10, 18))

        ret2 = croniter(
            seven_seconds_interval_pattern,
            start_time=datetime(2024, 7, 11, 10, 12),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret2, datetime(2024, 7, 11, 10, 19))

        ret3 = croniter(
            seven_seconds_interval_pattern,
            start_time=datetime(2024, 7, 11, 10, 11),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret3, datetime(2024, 7, 11, 10, 4))

        ret4 = croniter(
            seven_seconds_interval_pattern,
            start_time=datetime(2024, 7, 11, 10, 12),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret4, datetime(2024, 7, 11, 10, 5))

    def test_expand_from_start_time_hour(self):
        seven_hours_interval_pattern = '0 */7 * * *'
        ret1 = croniter(
            seven_hours_interval_pattern,
            start_time=datetime(2024, 7, 11, 15, 0),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret1, datetime(2024, 7, 11, 22, 0))

        ret2 = croniter(
            seven_hours_interval_pattern,
            start_time=datetime(2024, 7, 11, 16, 0),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret2, datetime(2024, 7, 11, 23, 0))

        ret3 = croniter(
            seven_hours_interval_pattern,
            start_time=datetime(2024, 7, 11, 15, 0),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret3, datetime(2024, 7, 11, 8, 0))

        ret4 = croniter(
            seven_hours_interval_pattern,
            start_time=datetime(2024, 7, 11, 16, 0),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret4, datetime(2024, 7, 11, 9, 0))

    def test_expand_from_start_time_date(self):
        five_days_interval_pattern = '0 0 */5 * *'
        ret1 = croniter(
            five_days_interval_pattern,
            start_time=datetime(2024, 7, 12),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret1, datetime(2024, 7, 17))

        ret2 = croniter(
            five_days_interval_pattern,
            start_time=datetime(2024, 7, 13),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret2, datetime(2024, 7, 18))

        ret3 = croniter(
            five_days_interval_pattern,
            start_time=datetime(2024, 7, 12),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret3, datetime(2024, 7, 7))

        ret4 = croniter(
            five_days_interval_pattern,
            start_time=datetime(2024, 7, 13),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret4, datetime(2024, 7, 8))

    def test_expand_from_start_time_month(self):
        three_monts_interval_pattern = '0 0 1 */3 *'
        ret1 = croniter(
            three_monts_interval_pattern,
            start_time=datetime(2024, 7, 1),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret1, datetime(2024, 10, 1))

        ret2 = croniter(
            three_monts_interval_pattern,
            start_time=datetime(2024, 8, 1),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret2, datetime(2024, 11, 1))

        ret3 = croniter(
            three_monts_interval_pattern,
            start_time=datetime(2024, 7, 1),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret3, datetime(2024, 4, 1))

        ret4 = croniter(
            three_monts_interval_pattern,
            start_time=datetime(2024, 8, 1),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret4, datetime(2024, 5, 1))

    def test_expand_from_start_time_day_of_week(self):
        three_monts_interval_pattern = '0 0 * * */2'
        ret1 = croniter(
            three_monts_interval_pattern,
            start_time=datetime(2024, 7, 10),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret1, datetime(2024, 7, 12))

        ret2 = croniter(
            three_monts_interval_pattern,
            start_time=datetime(2024, 7, 11),
            expand_from_start_time=True,
        ).get_next(datetime)
        assert_equal(ret2, datetime(2024, 7, 13))

        ret3 = croniter(
            three_monts_interval_pattern,
            start_time=datetime(2024, 7, 10),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret3, datetime(2024, 7, 8))

        ret4 = croniter(
            three_monts_interval_pattern,
            start_time=datetime(2024, 7, 11),
            expand_from_start_time=True,
        ).get_prev(datetime)
        assert_equal(ret4, datetime(2024, 7, 9))

    def test_get_next_fails_with_expand_from_start_time_true(self):
        expanded_croniter = croniter('0 0 */5 * *', expand_from_start_time=True)
        assert_raises(
            ValueError,
            expanded_croniter.get_next,
            datetime,
            start_time=datetime(2024, 7, 12),
        )

    def test_get_next_update_current(self):
        cron = croniter('* * * * * *')

        cron.set_current(datetime(2024, 7, 12), force=True)
        retn = [(cron.get_next(datetime), cron.get_current(datetime)) for a in range(3)]
        assert_equal(
            retn,
            [
                (datetime(2024, 7, 12, 0, 0, 1), datetime(2024, 7, 12, 0, 0, 1)),
                (datetime(2024, 7, 12, 0, 0, 2), datetime(2024, 7, 12, 0, 0, 2)),
                (datetime(2024, 7, 12, 0, 0, 3), datetime(2024, 7, 12, 0, 0, 3)),
            ],
        )

        retns = (
            cron.get_next(datetime, start_time=datetime(2024, 7, 12)),
            cron.get_current(datetime),
        )
        assert_equal(retn[0], retns)

        cron.set_current(datetime(2024, 7, 12), force=True)
        retp = [(cron.get_prev(datetime), cron.get_current(datetime)) for a in range(3)]
        assert_equal(
            retp,
            [
                (datetime(2024, 7, 11, 23, 59, 59), datetime(2024, 7, 11, 23, 59, 59)),
                (datetime(2024, 7, 11, 23, 59, 58), datetime(2024, 7, 11, 23, 59, 58)),
                (datetime(2024, 7, 11, 23, 59, 57), datetime(2024, 7, 11, 23, 59, 57)),
            ],
        )

        retps = (
            cron.get_prev(datetime, start_time=datetime(2024, 7, 12)),
            cron.get_current(datetime),
        )
        assert_equal(retp[0], retps)

        cron.set_current(datetime(2024, 7, 12), force=True)
        r = cron.all_next(datetime)
        retan = [(next(r), cron.get_current(datetime)) for a in range(3)]

        r = cron.all_next(datetime, start_time=datetime(2024, 7, 12))
        retans = [(next(r), cron.get_current(datetime)) for a in range(3)]

        cron.set_current(datetime(2024, 7, 12), force=True)
        r = cron.all_prev(datetime)
        retap = [(next(r), cron.get_current(datetime)) for a in range(3)]

        r = cron.all_prev(datetime, start_time=datetime(2024, 7, 12))
        retaps = [(next(r), cron.get_current(datetime)) for a in range(3)]

        assert_equal(retp, retap)
        assert_equal(retp, retaps)
        assert_equal(retn, retan)
        assert_equal(retn, retans)

        cron.set_current(datetime(2024, 7, 12), force=True)
        uretn = [
            (cron.get_next(datetime, update_current=False), cron.get_current(datetime))
            for a in range(3)
        ]
        assert_equal(
            uretn,
            [
                (datetime(2024, 7, 12, 0, 0, 1), datetime(2024, 7, 12, 0, 0)),
                (datetime(2024, 7, 12, 0, 0, 1), datetime(2024, 7, 12, 0, 0)),
                (datetime(2024, 7, 12, 0, 0, 1), datetime(2024, 7, 12, 0, 0)),
            ],
        )

        cron.set_current(datetime(2024, 7, 12), force=True)
        uretp = [
            (cron.get_prev(datetime, update_current=False), cron.get_current(datetime))
            for a in range(3)
        ]
        assert_equal(
            uretp,
            [
                (datetime(2024, 7, 11, 23, 59, 59), datetime(2024, 7, 12, 0, 0)),
                (datetime(2024, 7, 11, 23, 59, 59), datetime(2024, 7, 12, 0, 0)),
                (datetime(2024, 7, 11, 23, 59, 59), datetime(2024, 7, 12, 0, 0)),
            ],
        )

        cron.set_current(datetime(2024, 7, 12), force=True)
        r = cron.all_next(datetime, update_current=False)
        uretan = [(next(r), cron.get_current(datetime)) for a in range(3)]

        cron.set_current(datetime(2024, 7, 12), force=True)
        r = cron.all_prev(datetime, update_current=False)
        uretap = [(next(r), cron.get_current(datetime)) for a in range(3)]

        assert_equal(uretp, uretap)
        assert_equal(uretn, uretan)

    def test_issue_2038y(self):
        base = datetime(2040, 1, 1, 0, 0)
        itr = croniter('* * * * *', base)
        try:
            itr.get_next()
        except OverflowError:
            raise Exception('overflow not fixed!')

    def test_revert_issue_90_aka_support_DOW7(self):
        assert_true(croniter.is_valid('* * * * 1-7'))
        assert_true(croniter.is_valid('* * * * 7'))

    def test_sunday_ranges_to(self):
        self._test_sunday_ranges(
            '0 0 * * Sun-Sun',
            # fmt: off
            [
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Mon-Sun',
            # fmt: off
            [
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Tue-Sun',
            # fmt: off
            [
                2,
                3,
                4,
                5,
                6,
                7,
                9,
                10,
                11,
                12,
                13,
                14,
                16,
                17,
                18,
                19,
                20,
                21,
                23,
                24,
                25,
                26,
                27,
                28,
                30,
                31,
                1,
                2,
                3,
                4,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Wed-Sun',
            # fmt: off
            [
                3,
                4,
                5,
                6,
                7,
                10,
                11,
                12,
                13,
                14,
                17,
                18,
                19,
                20,
                21,
                24,
                25,
                26,
                27,
                28,
                31,
                1,
                2,
                3,
                4,
                7,
                8,
                9,
                10,
                11,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Thu-Sun',
            # fmt: off
            [
                4,
                5,
                6,
                7,
                11,
                12,
                13,
                14,
                18,
                19,
                20,
                21,
                25,
                26,
                27,
                28,
                1,
                2,
                3,
                4,
                8,
                9,
                10,
                11,
                15,
                16,
                17,
                18,
                22,
                23,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Fri-Sun',
            # fmt: off
            [
                5,
                6,
                7,
                12,
                13,
                14,
                19,
                20,
                21,
                26,
                27,
                28,
                2,
                3,
                4,
                9,
                10,
                11,
                16,
                17,
                18,
                23,
                24,
                25,
                1,
                2,
                3,
                8,
                9,
                10,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Sat-Sun',
            # fmt: off
            [
                6,
                7,
                13,
                14,
                20,
                21,
                27,
                28,
                3,
                4,
                10,
                11,
                17,
                18,
                24,
                25,
                2,
                3,
                9,
                10,
                16,
                17,
                23,
                24,
                30,
                31,
                6,
                7,
                13,
                14,
            ],
            # fmt: on
        )

    def test_sunday_ranges_from(self):
        self._test_sunday_ranges(
            '0 0 * * Sun-Mon',
            # fmt: off
            [
                7,
                8,
                14,
                15,
                21,
                22,
                28,
                29,
                4,
                5,
                11,
                12,
                18,
                19,
                25,
                26,
                3,
                4,
                10,
                11,
                17,
                18,
                24,
                25,
                31,
                1,
                7,
                8,
                14,
                15,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Sun-Tue',
            # fmt: off
            [
                2,
                7,
                8,
                9,
                14,
                15,
                16,
                21,
                22,
                23,
                28,
                29,
                30,
                4,
                5,
                6,
                11,
                12,
                13,
                18,
                19,
                20,
                25,
                26,
                27,
                3,
                4,
                5,
                10,
                11,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Sun-Wed',
            # fmt: off
            [
                2,
                3,
                7,
                8,
                9,
                10,
                14,
                15,
                16,
                17,
                21,
                22,
                23,
                24,
                28,
                29,
                30,
                31,
                4,
                5,
                6,
                7,
                11,
                12,
                13,
                14,
                18,
                19,
                20,
                21,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Sun-Thu',
            # fmt: off
            [
                2,
                3,
                4,
                7,
                8,
                9,
                10,
                11,
                14,
                15,
                16,
                17,
                18,
                21,
                22,
                23,
                24,
                25,
                28,
                29,
                30,
                31,
                1,
                4,
                5,
                6,
                7,
                8,
                11,
                12,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Sun-Fri',
            # fmt: off
            [
                2,
                3,
                4,
                5,
                7,
                8,
                9,
                10,
                11,
                12,
                14,
                15,
                16,
                17,
                18,
                19,
                21,
                22,
                23,
                24,
                25,
                26,
                28,
                29,
                30,
                31,
                1,
                2,
                4,
                5,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Sun-Sat',
            # fmt: off
            [
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Thu-Tue/2',
            # fmt: off
            [
                2,
                4,
                6,
                9,
                11,
                13,
                16,
                18,
                20,
                23,
                25,
                27,
                30,
                1,
                3,
                6,
                8,
                10,
                13,
                15,
                17,
                20,
                22,
                24,
                27,
                29,
                2,
                5,
                7,
                9,
            ],
            # fmt: on
        )

        self._test_sunday_ranges(
            '0 0 * * Thu-Tue/3',
            # fmt: off
            [
                4,
                7,
                11,
                14,
                18,
                21,
                25,
                28,
                1,
                4,
                8,
                11,
                15,
                18,
                22,
                25,
                29,
                3,
                7,
                10,
                14,
                17,
                21,
                24,
                28,
                31,
                4,
                7,
                11,
                14,
            ],
            # fmt: on
        )

    def test_mth_ranges_from(self):
        self._test_mth_cron_ranges(
            '0 0 1 Jan-Dec *',
            # fmt: off
            [
                '24 2',
                '24 3',
                '24 4',
                '24 5',
                '24 6',
                '24 7',
                '24 8',
                '24 9',
                '24 10',
                '24 11',
                '24 12',
                '25 1',
                '25 2',
                '25 3',
                '25 4',
                '25 5',
            ],
            # fmt: on
        )
        self._test_mth_cron_ranges(
            '0 0 1 Nov-Mar *',
            # fmt: off
            [
                '24 2',
                '24 3',
                '24 11',
                '24 12',
                '25 1',
                '25 2',
                '25 3',
                '25 11',
                '25 12',
                '26 1',
                '26 2',
                '26 3',
                '26 11',
                '26 12',
                '27 1',
                '27 2',
            ],
            # fmt: on
        )
        self._test_mth_cron_ranges(
            '0 0 1 Apr-Feb *',
            # fmt: off
            [
                '24 2',
                '24 4',
                '24 5',
                '24 6',
                '24 7',
                '24 8',
                '24 9',
                '24 10',
                '24 11',
                '24 12',
                '25 1',
                '25 2',
                '25 4',
                '25 5',
                '25 6',
                '25 7',
            ],
            # fmt: on
        )
        self._test_mth_cron_ranges(
            '0 0 1 Apr-Mar/3 *',
            # fmt: off
            [
                '24 4',
                '24 7',
                '24 10',
                '25 1',
                '25 4',
                '25 7',
                '25 10',
                '26 1',
                '26 4',
                '26 7',
                '26 10',
                '27 1',
                '27 4',
                '27 7',
                '27 10',
                '28 1',
            ],
            # fmt: on
        )
        self._test_mth_cron_ranges(
            '0 0 1 Apr-Mar/2 *',
            # fmt: off
            [
                '24 3',
                '24 4',
                '24 6',
                '24 8',
                '24 10',
                '24 12',
                '25 3',
                '25 4',
                '25 6',
                '25 8',
                '25 10',
                '25 12',
                '26 3',
                '26 4',
                '26 6',
                '26 8',
            ],
            # fmt: on
        )
        self._test_mth_cron_ranges(
            '0 0 1 Jan-Aug/2 *',
            # fmt: off
            [
                '24 3',
                '24 5',
                '24 7',
                '25 1',
                '25 3',
                '25 5',
                '25 7',
                '26 1',
                '26 3',
                '26 5',
                '26 7',
                '27 1',
                '27 3',
                '27 5',
                '27 7',
                '28 1',
            ],
            # fmt: on
        )
        self._test_mth_cron_ranges(
            '0 0 1 Jan-Aug/4 *',
            # fmt: off
            [
                '24 5',
                '25 1',
                '25 5',
                '26 1',
                '26 5',
                '27 1',
                '27 5',
                '28 1',
                '28 5',
                '29 1',
                '29 5',
                '30 1',
                '30 5',
                '31 1',
                '31 5',
                '32 1',
            ],
            # fmt: on
        )

    def _test_cron_ranges(
        self, expr, wanted, generator=None, loops=None, start=None, is_prev=None
    ):
        rets = (generator or gen_x_results)(
            expr,
            loops=loops or 10,
            start=start or datetime(2024, 1, 1),
            is_prev=is_prev,
        )
        for ret in rets:
            assert_equal(wanted, ret)

    def _test_mth_cron_ranges(self, expr, wanted, loops=None, start=None, is_prev=None):
        return self._test_cron_ranges(
            expr,
            wanted,
            generator=gen_x_mth_results,
            loops=loops or 16,
            start=start,
            is_prev=is_prev,
        )

    def _test_sunday_ranges(self, expr, wanted, loops=None, start=None, is_prev=None):
        return self._test_cron_ranges(
            expr,
            wanted,
            generator=gen_all_sunday_forms,
            loops=loops or 30,
            start=start,
            is_prev=is_prev,
        )


def gen_x_mth_results(expr, loops=None, start=None, is_prev=None):
    start = start or datetime(2024, 1, 1)
    cron = croniter(expr, start_time=start)
    n = cron.get_prev if is_prev else cron.get_next
    return [
        [
            f'{str(a.year)[-2:]} {a.month}'
            for a in [n(datetime) for i in range(loops or 16)]
        ]
    ]


def gen_x_results(expr, loops=None, start=None, is_prev=None):
    start = start or datetime(2024, 1, 1)
    cron = croniter(expr, start_time=start)
    n = cron.get_prev if is_prev else cron.get_next
    return [[a.isoformat() for a in [n(datetime) for i in range(loops or 30)]]]


def gen_all_sunday_forms(expr, loops=None, start=None, is_prev=None):
    start = start or datetime(2024, 1, 1)
    cron = croniter(expr, start_time=start)
    n = cron.get_prev if is_prev else cron.get_next
    ret1 = [a.day for a in [n(datetime) for i in range(loops or 30)]]
    cron = croniter(expr.lower().replace('sun', '7'), start_time=start)
    n = cron.get_prev if is_prev else cron.get_next
    ret2 = [a.day for a in [n(datetime) for i in range(loops or 30)]]
    cron = croniter(expr.lower().replace('sun', '0'), start_time=start)
    n = cron.get_prev if is_prev else cron.get_next
    ret3 = [a.day for a in [n(datetime) for i in range(loops or 30)]]
    return ret1, ret2, ret3
