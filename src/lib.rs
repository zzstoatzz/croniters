use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::OnceLock;

mod constants;
mod hash_expander;
mod utils;

pub fn get_croniters_version() -> &'static str {
    static CRONITERS_VERSION: OnceLock<String> = OnceLock::new();

    CRONITERS_VERSION.get_or_init(|| {
        // thank you pydantic-core for the snippet
        let version = env!("CARGO_PKG_VERSION");
        // cargo uses "1.0-alpha1" etc. while python uses "1.0.0a1", this is not full compatibility,
        // but it's good enough for now
        // see https://docs.rs/semver/1.0.9/semver/struct.Version.html#method.parse for rust spec
        // see https://peps.python.org/pep-0440/ for python spec
        // it seems the dot after "alpha/beta" e.g. "-alpha.1" is not necessary, hence why this works
        version.replace("-alpha", "a").replace("-beta", "b")
    })
}

#[pymodule]
fn _croniters(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", get_croniters_version())?;
    m.add("MINUTE_FIELD", constants::MINUTE_FIELD)?;
    m.add("HOUR_FIELD", constants::HOUR_FIELD)?;
    m.add("DAY_FIELD", constants::DAY_FIELD)?;
    m.add("MONTH_FIELD", constants::MONTH_FIELD)?;
    m.add("DOW_FIELD", constants::DOW_FIELD)?;
    m.add("SECOND_FIELD", constants::SECOND_FIELD)?;
    m.add("YEAR_FIELD", constants::YEAR_FIELD)?;
    m.add("M_ALPHAS", constants::M_ALPHAS.clone())?;
    m.add("DOW_ALPHAS", constants::DOW_ALPHAS.clone())?;
    m.add("UNIX_FIELDS", constants::UNIX_FIELDS)?;
    m.add("SECOND_FIELDS", constants::SECOND_FIELDS)?;
    m.add("YEAR_FIELDS", constants::YEAR_FIELDS)?;
    m.add("CRON_FIELDS", constants::CRON_FIELDS.clone())?;
    m.add("WEEKDAYS", constants::WEEKDAYS.clone())?;
    m.add("MONTHS", constants::MONTHS.clone())?;
    m.add("UNIX_CRON_LEN", constants::UNIX_CRON_LEN)?;
    m.add("SECOND_CRON_LEN", constants::SECOND_CRON_LEN)?;
    m.add("YEAR_CRON_LEN", constants::YEAR_CRON_LEN)?;
    m.add(
        "VALID_LEN_EXPRESSION",
        constants::VALID_LEN_EXPRESSION.clone(),
    )?;
    m.add("DAYS", constants::DAYS)?;
    m.add("RANGES", constants::RANGES)?;
    m.add("LEN_MEANS_ALL", constants::LEN_MEANS_ALL)?;
    m.add_function(wrap_pyfunction!(utils::is_32bit, m)?)?;
    m.add_function(wrap_pyfunction!(utils::is_leap, m)?)?;
    m.add_class::<hash_expander::HashExpander>()?;

    let py = m.py();
    let expanders = PyDict::new(py);
    expanders.set_item("hash", py.get_type::<hash_expander::HashExpander>())?;
    m.add("EXPANDERS", expanders)?;

    Ok(())
}
