use pyo3::prelude::*;

use std::collections::HashMap;

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

pub static WEEKDAYS: LazyLock<String> =
    LazyLock::new(|| DOW_ALPHAS.keys().map(|k| k.to_string()).collect());

pub static MONTHS: LazyLock<String> =
    LazyLock::new(|| M_ALPHAS.keys().map(|k| k.to_string()).collect());

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
