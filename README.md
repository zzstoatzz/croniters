# croniters

a port of python's [`croniter`](https://github.com/kiorky/croniter) package in Rust and exposed on PyPI via `pyo3` as [`croniters`](https://pypi.org/project/croniters/).


<details>
<summary>original usage docs</summary>

Usage
============

A simple example::

    >>> from croniter import croniter
    >>> from datetime import datetime
    >>> base = datetime(2010, 1, 25, 4, 46)
    >>> iter = croniter('*/5 * * * *', base)  # every 5 minutes
    >>> print(iter.get_next(datetime))   # 2010-01-25 04:50:00
    >>> print(iter.get_next(datetime))   # 2010-01-25 04:55:00
    >>> print(iter.get_next(datetime))   # 2010-01-25 05:00:00
    >>>
    >>> iter = croniter('2 4 * * mon,fri', base)  # 04:02 on every Monday and Friday
    >>> print(iter.get_next(datetime))   # 2010-01-26 04:02:00
    >>> print(iter.get_next(datetime))   # 2010-01-30 04:02:00
    >>> print(iter.get_next(datetime))   # 2010-02-02 04:02:00
    >>>
    >>> iter = croniter('2 4 1 * wed', base)  # 04:02 on every Wednesday OR on 1st day of month
    >>> print(iter.get_next(datetime))   # 2010-01-27 04:02:00
    >>> print(iter.get_next(datetime))   # 2010-02-01 04:02:00
    >>> print(iter.get_next(datetime))   # 2010-02-03 04:02:00
    >>>
    >>> iter = croniter('2 4 1 * wed', base, day_or=False)  # 04:02 on every 1st day of the month if it is a Wednesday
    >>> print(iter.get_next(datetime))   # 2010-09-01 04:02:00
    >>> print(iter.get_next(datetime))   # 2010-12-01 04:02:00
    >>> print(iter.get_next(datetime))   # 2011-06-01 04:02:00
    >>>
    >>> iter = croniter('0 0 * * sat#1,sun#2', base)  # 1st Saturday, and 2nd Sunday of the month
    >>> print(iter.get_next(datetime))   # 2010-02-06 00:00:00
    >>>
    >>> iter = croniter('0 0 * * 5#3,L5', base)  # 3rd and last Friday of the month
    >>> print(iter.get_next(datetime))   # 2010-01-29 00:00:00
    >>> print(iter.get_next(datetime))   # 2010-02-19 00:00:00


All you need to know is how to use the constructor and the ``get_next``
method, the signature of these methods are listed below::

    >>> def __init__(self, cron_format, start_time=time.time(), day_or=True)

croniter iterates along with ``cron_format`` from ``start_time``.
``cron_format`` is **min hour day month day_of_week**, you can refer to
http://en.wikipedia.org/wiki/Cron for more details. The ``day_or``
switch is used to control how croniter handles **day** and **day_of_week**
entries. Default option is the cron behaviour, which connects those
values using **OR**. If the switch is set to False, the values are connected
using **AND**. This behaves like fcron and enables you to e.g. define a job that
executes each 2nd Friday of a month by setting the days of month and the
weekday.
::

    >>> def get_next(self, ret_type=float)

get_next calculates the next value according to the cron expression and
returns an object of type ``ret_type``. ``ret_type`` should be a ``float`` or a
``datetime`` object.

Supported added for ``get_prev`` method. (>= 0.2.0)::

    >>> base = datetime(2010, 8, 25)
    >>> itr = croniter('0 0 1 * *', base)
    >>> print(itr.get_prev(datetime))  # 2010-08-01 00:00:00
    >>> print(itr.get_prev(datetime))  # 2010-07-01 00:00:00
    >>> print(itr.get_prev(datetime))  # 2010-06-01 00:00:00

You can validate your crons using ``is_valid`` class method. (>= 0.3.18)::

    >>> croniter.is_valid('0 0 1 * *')  # True
    >>> croniter.is_valid('0 wrong_value 1 * *')  # False

About DST
=========
Be sure to init your croniter instance with a TZ aware datetime for this to work!

Example using pytz::

    >>> import pytz
    >>> tz = pytz.timezone("Europe/Paris")
    >>> local_date = tz.localize(datetime(2017, 3, 26))
    >>> val = croniter('0 0 * * *', local_date).get_next(datetime)

Example using python_dateutil::

    >>> import dateutil.tz
    >>> tz = dateutil.tz.gettz('Asia/Tokyo')
    >>> local_date = datetime(2017, 3, 26, tzinfo=tz)
    >>> val = croniter('0 0 * * *', local_date).get_next(datetime)

Example using python built in module::

    >>> from datetime import datetime, timezone
    >>> local_date = datetime(2017, 3, 26, tzinfo=timezone.utc)
    >>> val = croniter('0 0 * * *', local_date).get_next(datetime)

About second repeats
=====================
Croniter is able to do second repetition crontabs form and by default seconds are the 6th field::

    >>> base = datetime(2012, 4, 6, 13, 26, 10)
    >>> itr = croniter('* * * * * 15,25', base)
    >>> itr.get_next(datetime) # 4/6 13:26:15
    >>> itr.get_next(datetime) # 4/6 13:26:25
    >>> itr.get_next(datetime) # 4/6 13:27:15

You can also note that this expression will repeat every second from the start datetime.::

    >>> croniter('* * * * * *', local_date).get_next(datetime)

You can also use seconds as first field::

    >>> itr = croniter('15,25 * * * * *', base, second_at_beginning=True)


About year
===========
Croniter also support year field.
Year presents at the seventh field, which is after second repetition.
The range of year field is from 1970 to 2099.
To ignore second repetition, simply set second to ``0`` or any other const::

    >>> base = datetime(2012, 4, 6, 2, 6, 59)
    >>> itr = croniter('0 0 1 1 * 0 2020/2', base)
    >>> itr.get_next(datetime) # 2020 1/1 0:0:0
    >>> itr.get_next(datetime) # 2022 1/1 0:0:0
    >>> itr.get_next(datetime) # 2024 1/1 0:0:0

Support for start_time shifts
==============================
See https://github.com/kiorky/croniter/pull/76,
You can set start_time=, then expand_from_start_time=True for your generations to be computed from start_time instead of calendar days::

    >>> from pprint import pprint
    >>> iter = croniter('0 0 */7 * *', start_time=datetime(2024, 7, 11), expand_from_start_time=True);pprint([iter.get_next(datetime) for a in range(10)])
    [datetime.datetime(2024, 7, 18, 0, 0),
     datetime.datetime(2024, 7, 25, 0, 0),
     datetime.datetime(2024, 8, 4, 0, 0),
     datetime.datetime(2024, 8, 11, 0, 0),
     datetime.datetime(2024, 8, 18, 0, 0),
     datetime.datetime(2024, 8, 25, 0, 0),
     datetime.datetime(2024, 9, 4, 0, 0),
     datetime.datetime(2024, 9, 11, 0, 0),
     datetime.datetime(2024, 9, 18, 0, 0),
     datetime.datetime(2024, 9, 25, 0, 0)]
    >>> # INSTEAD OF THE DEFAULT BEHAVIOR:
    >>> iter = croniter('0 0 */7 * *', start_time=datetime(2024, 7, 11), expand_from_start_time=False);pprint([iter.get_next(datetime) for a in range(10)])
    [datetime.datetime(2024, 7, 15, 0, 0),
     datetime.datetime(2024, 7, 22, 0, 0),
     datetime.datetime(2024, 7, 29, 0, 0),
     datetime.datetime(2024, 8, 1, 0, 0),
     datetime.datetime(2024, 8, 8, 0, 0),
     datetime.datetime(2024, 8, 15, 0, 0),
     datetime.datetime(2024, 8, 22, 0, 0),
     datetime.datetime(2024, 8, 29, 0, 0),
     datetime.datetime(2024, 9, 1, 0, 0),
     datetime.datetime(2024, 9, 8, 0, 0)]


Testing if a date matches a crontab
===================================
Test for a match with (>=0.3.32)::

    >>> croniter.match("0 0 * * *", datetime(2019, 1, 14, 0, 0, 0, 0))
    True
    >>> croniter.match("0 0 * * *", datetime(2019, 1, 14, 0, 2, 0, 0))
    False
    >>>
    >>> croniter.match("2 4 1 * wed", datetime(2019, 1, 1, 4, 2, 0, 0)) # 04:02 on every Wednesday OR on 1st day of month
    True
    >>> croniter.match("2 4 1 * wed", datetime(2019, 1, 1, 4, 2, 0, 0), day_or=False) # 04:02 on every 1st day of the month if it is a Wednesday
    False

Testing if a crontab matches in datetime range
==============================================
Test for a match_range with (>=2.0.3)::

    >>> croniter.match_range("0 0 * * *", datetime(2019, 1, 13, 0, 59, 0, 0), datetime(2019, 1, 14, 0, 1, 0, 0))
    True
    >>> croniter.match_range("0 0 * * *", datetime(2019, 1, 13, 0, 1, 0, 0), datetime(2019, 1, 13, 0, 59, 0, 0))
    False
    >>> croniter.match_range("2 4 1 * wed", datetime(2019, 1, 1, 3, 2, 0, 0), datetime(2019, 1, 1, 5, 1, 0, 0))
    # 04:02 on every Wednesday OR on 1st day of month
    True
    >>> croniter.match_range("2 4 1 * wed", datetime(2019, 1, 1, 3, 2, 0, 0), datetime(2019, 1, 1, 5, 2, 0, 0), day_or=False)
    # 04:02 on every 1st day of the month if it is a Wednesday
    False

Gaps between date matches
=========================
For performance reasons, croniter limits the amount of CPU cycles spent attempting to find the next match.
Starting in v0.3.35, this behavior is configurable via the ``max_years_between_matches`` parameter, and the default window has been increased from 1 year to 50 years.

The defaults should be fine for many use cases.
Applications that evaluate multiple cron expressions or handle cron expressions from untrusted sources or end-users should use this parameter.
Iterating over sparse cron expressions can result in increased CPU consumption or a raised ``CroniterBadDateError`` exception which indicates that croniter has given up attempting to find the next (or previous) match.
Explicitly specifying ``max_years_between_matches`` provides a way to limit CPU utilization and simplifies the iterable interface by eliminating the need for ``CroniterBadDateError``.
The difference in the iterable interface is based on the reasoning that whenever ``max_years_between_matches`` is explicitly agreed upon, there is no need for croniter to signal that it has given up; simply stopping the iteration is preferable.

This example matches 4 AM Friday, January 1st.
Since January 1st isn't often a Friday, there may be a few years between each occurrence.
Setting the limit to 15 years ensures all matches::

    >>> it = croniter("0 4 1 1 fri", datetime(2000,1,1), day_or=False, max_years_between_matches=15).all_next(datetime)
    >>> for i in range(5):
    ...     print(next(it))
    ...
    2010-01-01 04:00:00
    2016-01-01 04:00:00
    2021-01-01 04:00:00
    2027-01-01 04:00:00
    2038-01-01 04:00:00

However, when only concerned with dates within the next 5 years, simply set ``max_years_between_matches=5`` in the above example.
This will result in no matches found, but no additional cycles will be wasted on unwanted matches far in the future.

Iterating over a range using cron
=================================
Find matches within a range using the ``croniter_range()`` function.  This is much like the builtin ``range(start,stop,step)`` function, but for dates.  The `step` argument is a cron expression.
Added in (>=0.3.34)

List the first Saturday of every month in 2019::

    >>> from croniter import croniter_range
    >>> for dt in croniter_range(datetime(2019, 1, 1), datetime(2019, 12, 31), "0 0 * * sat#1"):
    >>>     print(dt)


Hashed expressions
==================

croniter supports Jenkins-style hashed expressions, using the "H" definition keyword and the required hash_id keyword argument.
Hashed expressions remain consistent, given the same hash_id, but different hash_ids will evaluate completely different to each other.
This allows, for example, for an even distribution of differently-named jobs without needing to manually spread them out.

    >>> itr = croniter("H H * * *", hash_id="hello")
    >>> itr.get_next(datetime)
    datetime.datetime(2021, 4, 10, 11, 10)
    >>> itr.get_next(datetime)
    datetime.datetime(2021, 4, 11, 11, 10)
    >>> itr = croniter("H H * * *", hash_id="hello")
    >>> itr.get_next(datetime)
    datetime.datetime(2021, 4, 10, 11, 10)
    >>> itr = croniter("H H * * *", hash_id="bonjour")
    >>> itr.get_next(datetime)
    datetime.datetime(2021, 4, 10, 20, 52)


Random expressions
==================

Random "R" definition keywords are supported, and remain consistent only within their croniter() instance.

    >>> itr = croniter("R R * * *")
    >>> itr.get_next(datetime)
    datetime.datetime(2021, 4, 10, 22, 56)
    >>> itr.get_next(datetime)
    datetime.datetime(2021, 4, 11, 22, 56)
    >>> itr = croniter("R R * * *")
    >>> itr.get_next(datetime)
    datetime.datetime(2021, 4, 11, 4, 19)


Note about Ranges
=================

Note that as a deviation from cron standard, croniter is somehow laxist with ranges and will allow ranges of ``Jan-Dec``, & ``Sun-Sat`` in reverse way and interpret them as following examples:

    - ``Apr-Jan``: from April to january
    - ``Sat-Sun``: Saturday, Sunday
    - ``Wed-Sun``: Wednesday to Saturday, Sunday

Please note that if a /step is given, it will be respected.

Note about Sunday
=================

Note that as a deviation from cron standard, croniter like numerous cron implementations supports ``SUNDAY`` to be expressed as ``DAY7``, allowing such expressions:

    - ``0 0 * * 7``
    - ``0 0 * * 6-7``
    - ``0 0 * * 6,7``


Keyword expressions
===================

Vixie cron-style "@" keyword expressions are supported.
What they evaluate to depends on whether you supply hash_id: no hash_id corresponds to Vixie cron definitions (exact times, minute resolution), while with hash_id corresponds to Jenkins definitions (hashed within the period, second resolution).

    ============ ============ ================
    Keyword      No hash_id   With hash_id
    ============ ============ ================
    @midnight    0 0 * * *    H H(0-2) * * * H
    @hourly      0 * * * *    H * * * * H
    @daily       0 0 * * *    H H * * * H
    @weekly      0 0 * * 0    H H * * H H
    @monthly     0 0 1 * *    H H H * * H
    @yearly      0 0 1 1 *    H H H H * H
    @annually    0 0 1 1 *    H H H H * H
    ============ ============ ================


</details>

## Overview

`croniters` intends to be a drop-in replacement for the python [`croniter`](https://github.com/kiorky/croniter) package, implemented in Rust.

> [!IMPORTANT]
> I say "intends to" because while the test suite is ported and should cover the majority of cases, there may be subtle differences between rust and python implementations.


## Why?
`croniter` is no longer maintained and everyone vendoring means more collective toil.

rust already has good datetime support and rust types are great for this sort of pedantry.

## Project Roadmap

- port everything to rust incrementally, maintaining the public `croniter` API.
- consider deprecating things that don't make coherent sense.

### Phase 0: Setup
- [x] get pyo3 setup
- [x] port test suite from croniter
- [ ] move constants and simple utils to rust

### Phase 1: Core Functionality

Initial implementation focusing on the most commonly used features:

- Basic cron expression parsing
- `get_next()`/`get_prev()` methods
- DateTime/timestamp conversions
- Support for basic cron formats (5-field Unix cron)

### Phase 2: Extended Features

Add support for:

- Second and year fields (6 and 7-field formats)
- Hash-based expressions
- Range iteration (`croniter_range`)
- All croniter expression aliases (@yearly, @monthly, etc)

### Phase 3: Full Compatibility

Complete feature parity with croniter:

- All edge cases and special syntax
- Full timezone support
- Complete test suite port


> [!WARNING]
> Not seeing something important in the roadmap? [Open an issue](https://github.com/zzstoatzz/croniters/issues) and I'll add it!

## (Planned) Technical Stack

- **Cron Parsing**: `cron` crate
- **Python Bindings**: `pyo3`
- **Build System**: `maturin`

## Contributing

Please do - I am only learning rust and pyo3! See the [justfile](justfile) for details on running locally.

## License

Same as croniter - MIT License 

## Acknowledgements

- [croniter](https://github.com/kiorky/croniter) - original implementation
- [pyo3](https://github.com/pyo3/pyo3) - Python bindings
- [maturin](https://github.com/PyO3/maturin) - build system


