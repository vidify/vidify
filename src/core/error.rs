//! TODO: module-level docs

pub type Result<T> = std::result::Result<T, Error>;

/// The different errors that may happen are stored in this enum. These
/// include errors specific to some APIs because that way they can be handled
/// correctly.
#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("Failed parsing the configuration: {0}")]
    ConfigParse(#[from] structconf::Error),
    #[error("I/O error: {0}")]
    IO(#[from] std::io::Error),
}

/// For Python interoperability
impl From<Error> for pyo3::PyErr {
    fn from(err: Error) -> pyo3::PyErr {
        pyo3::exceptions::PyOSError::new_err(err.to_string())
    }
}
