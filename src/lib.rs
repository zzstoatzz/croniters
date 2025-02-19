use pyo3::prelude::*;

mod constants;

/// A Python module implemented in Rust.
#[pymodule]
fn _croniters(m: &Bound<'_, PyModule>) -> PyResult<()> {
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
    Ok(())
}
