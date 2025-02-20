use pyo3::prelude::*;

use std::collections::{HashMap, HashSet};

use std::sync::LazyLock;
pub const MINUTE_FIELD: i32 = 0;
pub const HOUR_FIELD: i32 = 1;
pub const DAY_FIELD: i32 = 2;
pub const MONTH_FIELD: i32 = 3;
pub const DOW_FIELD: i32 = 4;
pub const SECOND_FIELD: i32 = 5;
pub const YEAR_FIELD: i32 = 6;

pub static M_ALPHAS: LazyLock<HashMap<&'static str, i32>> = LazyLock::new(|| {
    HashMap::from([
        ("jan", 1),
        ("feb", 2),
        ("mar", 3),
        ("apr", 4),
        ("may", 5),
        ("jun", 6),
        ("jul", 7),
        ("aug", 8),
        ("sep", 9),
        ("oct", 10),
        ("nov", 11),
        ("dec", 12),
    ])
});

pub static DOW_ALPHAS: LazyLock<HashMap<&'static str, i32>> = LazyLock::new(|| {
    HashMap::from([
        ("sun", 0),
        ("mon", 1),
        ("tue", 2),
        ("wed", 3),
        ("thu", 4),
        ("fri", 5),
        ("sat", 6),
    ])
});

pub static WEEKDAYS: LazyLock<String> = LazyLock::new(|| {
    DOW_ALPHAS
        .keys()
        .map(|k| k.to_string())
        .collect::<Vec<_>>()
        .join("|")
});

pub static MONTHS: LazyLock<String> = LazyLock::new(|| {
    M_ALPHAS
        .keys()
        .map(|k| k.to_string())
        .collect::<Vec<_>>()
        .join("|")
});

pub const UNIX_FIELDS: [i32; 5] = [MINUTE_FIELD, HOUR_FIELD, DAY_FIELD, MONTH_FIELD, DOW_FIELD];

pub const SECOND_FIELDS: [i32; 6] = [
    MINUTE_FIELD,
    HOUR_FIELD,
    DAY_FIELD,
    MONTH_FIELD,
    DOW_FIELD,
    SECOND_FIELD,
];

pub const YEAR_FIELDS: [i32; 7] = [
    MINUTE_FIELD,
    HOUR_FIELD,
    DAY_FIELD,
    MONTH_FIELD,
    DOW_FIELD,
    SECOND_FIELD,
    YEAR_FIELD,
];

pub const DAYS: [i32; 12] = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

pub const RANGES: [(i32, i32); 7] = [
    (0, 59),      // minutes
    (0, 23),      // hours
    (1, 31),      // days
    (1, 12),      // months
    (0, 6),       // weekdays
    (0, 59),      // seconds
    (1970, 2099), // years
];

#[derive(Eq, Hash, PartialEq, Clone, IntoPyObject)]
pub enum CronFieldKeyType {
    Str(&'static str),
    Int(usize),
}

pub static CRON_FIELDS: LazyLock<HashMap<CronFieldKeyType, &'static [i32]>> = LazyLock::new(|| {
    HashMap::from([
        (CronFieldKeyType::Str("unix"), &UNIX_FIELDS[..]),
        (CronFieldKeyType::Str("second"), &SECOND_FIELDS[..]),
        (CronFieldKeyType::Str("year"), &YEAR_FIELDS[..]),
        (CronFieldKeyType::Int(UNIX_FIELDS.len()), &UNIX_FIELDS[..]),
        (
            CronFieldKeyType::Int(SECOND_FIELDS.len()),
            &SECOND_FIELDS[..],
        ),
        (CronFieldKeyType::Int(YEAR_FIELDS.len()), &YEAR_FIELDS[..]),
    ])
});

pub const UNIX_CRON_LEN: usize = UNIX_FIELDS.len();
pub const SECOND_CRON_LEN: usize = SECOND_FIELDS.len();
pub const YEAR_CRON_LEN: usize = YEAR_FIELDS.len();

// VALID_LEN_EXPRESSION = set(a for a in CRON_FIELDS if isinstance(a, int))
pub static VALID_LEN_EXPRESSION: LazyLock<HashSet<usize>> = LazyLock::new(|| {
    HashSet::from_iter(
        CRON_FIELDS
            .keys()
            .filter_map(|k| match k {
                CronFieldKeyType::Int(i) => Some(*i),
                CronFieldKeyType::Str(_) => None,
            })
            .collect::<Vec<_>>(),
    )
});

pub const LEN_MEANS_ALL: [i32; 7] = [
    60,  // minutes
    24,  // hours
    31,  // days
    12,  // months
    7,   // weekdays
    60,  // seconds
    130, // years
];
