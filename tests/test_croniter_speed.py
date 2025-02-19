import os
import sys
from datetime import datetime
from timeit import Timer

import pytest
import pytz
from croniters import croniter


def test_run_long(iterations=1):  # noqa: C901
    dt = datetime(2010, 1, 23, 12, 18)
    itr = croniter('*/1 * * * *', dt)
    for _ in range(iterations):  # ~ 58
        itr.get_next()

    itr = croniter('*/5 * * * *', dt)
    for _ in range(iterations):
        itr.get_next()

    dt = datetime(2010, 1, 24, 12, 2)
    itr = croniter('0 */3 * * *', dt)
    for _ in range(iterations):
        itr.get_next()

    dt = datetime(2010, 2, 24, 12, 9)
    itr = croniter('0 0 */3 * *', dt)
    for _ in range(iterations):
        itr.get_next(datetime)

    # test leap year
    dt = datetime(1996, 2, 27)
    itr = croniter('0 0 * * *', dt)
    for _ in range(iterations):
        itr.get_next(datetime)

    dt2 = datetime(2000, 2, 27)
    itr2 = croniter('0 0 * * *', dt2)
    for _ in range(iterations):
        itr2.get_next(datetime)

    dt = datetime(2010, 2, 25)
    itr = croniter('0 0 * * sat', dt)
    for _ in range(iterations):
        itr.get_next(datetime)

    dt = datetime(2010, 1, 25)
    itr = croniter('0 0 1 * wed', dt)
    for _ in range(iterations):
        itr.get_next(datetime)

    dt = datetime(2010, 1, 25)
    itr = croniter('0 0 1 * *', dt)
    for _ in range(iterations):
        itr.get_next()

    dt = datetime(2010, 8, 25, 15, 56)
    itr = croniter('*/1 * * * *', dt)
    for _ in range(iterations):
        itr.get_prev(datetime)

    dt = datetime(2010, 8, 25, 15, 0)
    itr = croniter('*/1 * * * *', dt)
    for _ in range(iterations):
        itr.get_prev(datetime)

    dt = datetime(2010, 8, 25, 0, 0)
    itr = croniter('*/1 * * * *', dt)
    for _ in range(iterations):
        itr.get_prev(datetime)

    dt = datetime(2010, 8, 25, 15, 56)
    itr = croniter('0 0 * * sat,sun', dt)
    for _ in range(iterations):
        itr.get_prev(datetime)

    dt = datetime(2010, 2, 25)
    itr = croniter('0 0 * * 7', dt)
    for _ in range(iterations):
        itr.get_prev(datetime)

    # dst regression test
    tz = pytz.timezone('Europe/Bucharest')
    offsets = set()
    dst_cron = '15 0,3 * 3 *'
    dst_iters = int(2 * 31 * (iterations / 40))
    dt = datetime(2010, 1, 25, tzinfo=tz)
    itr = croniter(dst_cron, dt)
    for _ in range(dst_iters):
        d = itr.get_next(datetime)
        offsets.add(d.utcoffset())
    itr = croniter(dst_cron, dt)
    for _ in range(dst_iters):
        d = itr.get_prev(datetime)
        offsets.add(d.utcoffset())


@pytest.mark.skipif(sys.version_info[0] < 3, reason='Python 2 not supported')
def test_not_long_time():
    iterations = int(os.environ.get('CRONITER_TEST_SPEED_ITERATIONS', '40'))

    # Create namespace for Timer
    namespace = {'run_long_test': test_run_long, 'iterations': iterations}

    t = Timer('run_long_test(iterations)', globals=namespace)
    limit = 80
    ret = t.timeit(limit)
    assert ret < limit, f'Regression in croniter speed detected ({ret} {limit}).'
