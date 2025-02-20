use crc32fast::hash;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use rand::Rng;
use regex::Regex;
use std::sync::OnceLock;

static HASH_EXPRESSION_RE: OnceLock<Regex> = OnceLock::new();

fn get_hash_expression_re() -> &'static Regex {
    HASH_EXPRESSION_RE.get_or_init(|| {
        Regex::new(r"^(?P<hash_type>[HhRr])\((?P<range_begin>\d+)-(?P<range_end>\d+)\)(?:/(?P<divisor>\d+))?$|^(?P<hash_type2>[HhRr])(?:/(?P<divisor2>\d+))?$").unwrap()
    })
}

#[pyclass]
pub struct HashExpander {
    #[pyo3(get)]
    cron: Py<PyAny>,
}

#[pymethods]
impl HashExpander {
    #[new]
    fn new(cronit: Py<PyAny>) -> Self {
        HashExpander { cron: cronit }
    }

    #[pyo3(signature = (idx, hash_type=None, hash_id=None, range_end=None, range_begin=None))]
    fn do_(
        &self,
        py: Python<'_>,
        idx: i32,
        hash_type: Option<&str>,
        hash_id: Option<&[u8]>,
        range_end: Option<i32>,
        range_begin: Option<i32>,
    ) -> PyResult<i32> {
        let ranges = self.cron.bind(py).getattr("RANGES")?;

        let range_end = match range_end {
            Some(end) => end,
            None => ranges.get_item(idx)?.get_item(1)?.extract()?,
        };

        let range_begin = match range_begin {
            Some(begin) => begin,
            None => ranges.get_item(idx)?.get_item(0)?.extract()?,
        };

        let crc = if hash_type == Some("r") {
            let mut rng = rand::rng();
            rng.random::<u32>()
        } else {
            hash(hash_id.unwrap_or_default())
        };

        Ok((((crc >> idx) % ((range_end - range_begin + 1) as u32)) as i32) + range_begin)
    }

    #[pyo3(signature = (_efl, _idx, expr, _hash_id=None, **_kwargs))]
    fn match_(
        &self,
        _py: Python<'_>,
        _efl: &Bound<'_, PyAny>,
        _idx: i32,
        expr: &str,
        _hash_id: Option<&[u8]>,
        _kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<bool> {
        Ok(get_hash_expression_re().is_match(expr))
    }

    #[pyo3(signature = (efl, idx, expr, hash_id=None, match_=None, **kwargs))]
    #[allow(clippy::too_many_arguments)]
    fn expand(
        &self,
        py: Python<'_>,
        efl: &Bound<'_, PyAny>,
        idx: i32,
        expr: &str,
        hash_id: Option<&[u8]>,
        match_: Option<bool>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<String> {
        let is_match = match match_ {
            Some(m) => m,
            None => self.match_(py, efl, idx, expr, hash_id, kwargs)?,
        };

        if !is_match {
            return Ok(expr.to_string());
        }

        let captures = get_hash_expression_re()
            .captures(expr)
            .ok_or_else(|| PyValueError::new_err("Failed to capture regex groups"))?;

        let hash_type = captures
            .name("hash_type")
            .or_else(|| captures.name("hash_type2"))
            .map(|m| m.as_str().to_ascii_lowercase())
            .unwrap_or_else(|| "h".to_string());

        if hash_type == "h" && hash_id.is_none() {
            return Err(PyValueError::new_err(
                "Hashed definitions must include hash_id",
            ));
        }

        if let (Some(begin), Some(end)) = (
            captures
                .name("range_begin")
                .map(|m| m.as_str().parse::<i32>().unwrap()),
            captures
                .name("range_end")
                .map(|m| m.as_str().parse::<i32>().unwrap()),
        ) {
            if begin >= end {
                return Err(PyValueError::new_err(
                    "Range end must be greater than range begin",
                ));
            }

            if let Some(divisor) = captures
                .name("divisor")
                .map(|m| m.as_str().parse::<i32>().unwrap())
            {
                if divisor == 0 {
                    return Err(PyValueError::new_err(format!("Bad expression: {expr}")));
                }

                Ok(format!(
                    "{}-{}/{}",
                    self.do_(
                        py,
                        idx,
                        Some(&hash_type),
                        hash_id,
                        Some(divisor - 1 + begin),
                        Some(begin)
                    )?,
                    end,
                    divisor
                ))
            } else {
                Ok(self
                    .do_(py, idx, Some(&hash_type), hash_id, Some(end), Some(begin))?
                    .to_string())
            }
        } else if let Some(divisor) = captures
            .name("divisor")
            .or_else(|| captures.name("divisor2"))
            .map(|m| m.as_str().parse::<i32>().unwrap())
        {
            if divisor == 0 {
                return Err(PyValueError::new_err(format!("Bad expression: {expr}")));
            }

            let ranges = self.cron.bind(py).getattr("RANGES")?;
            let range_begin: i32 = ranges.get_item(idx)?.get_item(0)?.extract()?;
            let range_end: i32 = ranges.get_item(idx)?.get_item(1)?.extract()?;

            Ok(format!(
                "{}-{}/{}",
                self.do_(
                    py,
                    idx,
                    Some(&hash_type),
                    hash_id,
                    Some(divisor - 1 + range_begin),
                    Some(range_begin)
                )?,
                range_end,
                divisor
            ))
        } else {
            Ok(self
                .do_(py, idx, Some(&hash_type), hash_id, None, None)?
                .to_string())
        }
    }
}
