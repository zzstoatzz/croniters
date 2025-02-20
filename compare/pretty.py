import time
from datetime import datetime

import croniter as original_croniter
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

import croniters as my_croniter

N_ITERATIONS = 100

TEST_EXPRESSIONS = [
    '*/5 * * * *',  # every 5 minutes
    '0 */2 * * *',  # every 2 hours
    '0 0 1 */3 *',  # first of every 3rd month
    '0 0 * * sat#1',  # first Saturday
    '0 0 L * *',  # last day of month
    'H * * * *',  # random minute every hour
    'H H * * *',  # random minute, random hour every day
    'H(30-59) * * * *',  # random minute in range
    'H * H/2 * *',  # every other day (random)
    '@midnight',  # built-in hash expression
]

# Benchmark functions: each takes (module, base_time, …) so they can be run uniformly.


def benchmark_basic_iteration(module, base_time, iterations=N_ITERATIONS):
    for _ in range(iterations):
        itr = module('0 0 * * *', base_time)
        itr.get_next(datetime)


def benchmark_expression_validation(
    module, base_time, test_expressions, iterations=N_ITERATIONS
):
    # base_time not used here.
    for expr in test_expressions * iterations:
        module.is_valid(expr)


def benchmark_date_range_matching(module, base_time, iterations=N_ITERATIONS):
    end = datetime.now()
    for _ in range(iterations):
        module.match_range('0 * * * *', base_time, end)


def benchmark_next_prev_dates(module, base_time, iterations=N_ITERATIONS):
    itr = module('0 0 * * *', base_time)
    for _ in range(iterations):
        itr.get_next(datetime)
        itr.get_prev(datetime)


def benchmark_all_operations(
    module, base_time, test_expressions, iterations=N_ITERATIONS
):
    # Basic iteration
    itr = module('0 0 * * *', base_time)
    for _ in range(iterations):
        itr.get_next(datetime)
    # Expression validation
    for expr in test_expressions * iterations:
        module.is_valid(expr)
    # Range matching
    end = datetime.now()
    for _ in range(iterations):
        module.match_range('0 * * * *', base_time, end)
    # Next/prev dates
    itr = module('0 0 * * *', base_time)
    for _ in range(iterations):
        itr.get_next(datetime)
        itr.get_prev(datetime)


def benchmark_hash_operations(module, base_time, iterations=N_ITERATIONS):
    """Test hash-specific operations"""
    hash_id = b'test_hash_id'
    itr = module('H H * * *', base_time, hash_id=hash_id)
    for _ in range(iterations):
        itr.get_next(datetime)
        itr.get_prev(datetime)


def benchmark_hash_range_operations(module, base_time, iterations=N_ITERATIONS):
    """Test hash range operations"""
    hash_id = b'test_hash_id'
    itr = module('H(30-59)/10 H * * *', base_time, hash_id=hash_id)
    for _ in range(iterations):
        itr.get_next(datetime)


# Simple benchmark runner: runs a function multiple rounds and collects timing info.
def run_benchmark(test_func, mod, base_time, **kwargs):
    total = 0
    iterations = kwargs.get('iterations', N_ITERATIONS)

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            f'[cyan]Running {test_func.__name__} for {iterations} iterations...',
            total=iterations,
        )

        for _ in range(iterations):
            start = time.perf_counter()
            test_func(mod, base_time, **kwargs)
            total += time.perf_counter() - start
            progress.advance(task)

    return total, total / iterations


def main():
    console = Console()

    with console.status('[bold green]Setting up benchmark...') as status:
        base_time = datetime.now()
        modules = [
            ('original', original_croniter.croniter),
            ('rust', my_croniter.croniter),
        ]
        tests = [
            (
                'Basic Iteration',
                benchmark_basic_iteration,
                {'iterations': N_ITERATIONS},
            ),
            (
                'Expression Validation',
                benchmark_expression_validation,
                {'iterations': N_ITERATIONS, 'test_expressions': TEST_EXPRESSIONS},
            ),
            (
                'Date Range Matching',
                benchmark_date_range_matching,
                {'iterations': N_ITERATIONS},
            ),
            (
                'Next/Prev Dates',
                benchmark_next_prev_dates,
                {'iterations': N_ITERATIONS},
            ),
            (
                'All Operations',
                benchmark_all_operations,
                {'iterations': 100, 'test_expressions': TEST_EXPRESSIONS},
            ),
            (
                'Hash Operations',
                benchmark_hash_operations,
                {'iterations': N_ITERATIONS},
            ),
            (
                'Hash Range Operations',
                benchmark_hash_range_operations,
                {'iterations': N_ITERATIONS},
            ),
        ]

        table = Table(title='[bold]Croniter Benchmark Results[/bold]')
        table.add_column('Module', style='cyan', no_wrap=True)
        table.add_column('Test', style='magenta')
        table.add_column('Total Time (s)', justify='right', style='green')
        table.add_column('Avg Time per Round (s)', justify='right', style='yellow')

    for mod_name, mod in modules:
        console.print(f'\n[bold blue]Testing {mod_name} implementation[/bold blue]')
        for test_name, test_func, kwargs in tests:
            status.update(f'[bold yellow]Running {test_name}...[/bold yellow]')
            total, avg = run_benchmark(test_func, mod, base_time, **kwargs)
            table.add_row(mod_name, test_name, f'{total:.6f}', f'{avg:.6f}')

    console.print('\n')
    console.print(table)


if __name__ == '__main__':
    main()
