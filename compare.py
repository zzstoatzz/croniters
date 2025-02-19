from datetime import datetime

import croniter as original_croniter
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

import croniters as my_croniter


@pytest.fixture
def base_time():
    return datetime.now()


@pytest.fixture
def test_expressions():
    return [
        '*/5 * * * *',  # every 5 minutes
        '0 */2 * * *',  # every 2 hours
        '0 0 1 */3 *',  # first of every 3rd month
        '0 0 * * sat#1',  # first Saturday
        '0 0 L * *',  # last day of month
    ]


def test_basic_iteration(benchmark: BenchmarkFixture, base_time: datetime):
    def run(module):
        for _ in range(1000):
            iter = module('0 0 * * *', base_time)
            iter.get_next(datetime)

    benchmark.pedantic(
        run,
        args=(original_croniter.croniter,),
        iterations=1,
        rounds=100,
    )


def test_expression_validation(
    benchmark: BenchmarkFixture, test_expressions: list[str]
):
    def run(module):
        for expr in test_expressions * 1000:
            module.is_valid(expr)

    benchmark.pedantic(
        run,
        args=(original_croniter.croniter,),
        iterations=1,
        rounds=100,
    )


def test_date_range_matching(benchmark: BenchmarkFixture, base_time: datetime):
    end = datetime.now()

    def run(module):
        for _ in range(1000):
            module.match_range('0 * * * *', base_time, end)

    benchmark.pedantic(
        run,
        args=(original_croniter.croniter,),
        iterations=1,
        rounds=100,
    )


def test_next_prev_dates(benchmark: BenchmarkFixture, base_time: datetime):
    def run(module):
        iter = module('0 0 * * *', base_time)
        for _ in range(1000):
            iter.get_next(datetime)
            iter.get_prev(datetime)

    benchmark.pedantic(
        run,
        args=(original_croniter.croniter,),
        iterations=1,
        rounds=100,
    )


@pytest.mark.parametrize(
    'module',
    [
        pytest.param(original_croniter.croniter, id='original'),
        pytest.param(my_croniter.croniter, id='rust'),
    ],
)
def test_all_operations(
    module,
    benchmark: BenchmarkFixture,
    base_time: datetime,
    test_expressions: list[str],
):
    """Compare overall performance of all common operations"""
    end = datetime.now()

    def run():
        # Basic iteration
        iter = module('0 0 * * *', base_time)
        for _ in range(100):
            iter.get_next(datetime)

        # Expression validation
        for expr in test_expressions * 100:
            module.is_valid(expr)

        # Range matching
        for _ in range(100):
            module.match_range('0 * * * *', base_time, end)

        # Next/prev dates
        iter = module('0 0 * * *', base_time)
        for _ in range(100):
            iter.get_next(datetime)
            iter.get_prev(datetime)

    benchmark(run)
