//! TODO: module-level docs

use crate::error::Result;

use std::fs::{create_dir, File};
use std::ops::Deref;
use std::path::PathBuf;

use dirs::*;
use pyo3::prelude::*;

#[pymodule]
fn res(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<Res>()?;
    m.add_class::<ResKind>()?;

    Ok(())
}

/// What kind of resource it is, to determine where it should be stored. The
/// custom type holds the full path, the rest of them only contain the file
/// name, which will be appended to a predetermined directory.
#[pyenum]
#[derive(Clone)]
pub enum ResKind {
    /// Can be anything, no path is appended to it.
    Custom,
    /// Holds configuration files, like `~/.config/vidify/config.ini`.
    Config,
    /// Holds persistent data for the user, like
    /// `~/.local/share/vidify/session.log`.
    Data,
    /// Holds resources for the app, which should be in the install location.
    Resource,
}

/// The actual struct with the functionalities required to initialize the
/// resource's path and access to them.
#[pyclass]
#[derive(Clone)]
pub struct Res {
    #[pyo3(get)]
    pub kind: ResKind,
    #[pyo3(get)]
    pub path: String,
}

#[pymethods]
impl Res {
    #[new]
    pub fn new(kind: ResKind, path: &str) -> Result<Self> {
        use std::io::{Error, ErrorKind};
        use ResKind::*;

        let path = match kind {
            Custom => path.to_string(),
            Config => Self::custom(
                &mut config_dir().ok_or_else(|| Error::new(ErrorKind::NotFound, "config dir"))?,
                path,
            )?,
            Data => Self::custom(
                &mut data_dir().ok_or_else(|| Error::new(ErrorKind::NotFound, "data dir"))?,
                path,
            )?,
            Resource => Self::custom(
                &mut data_dir().ok_or_else(|| Error::new(ErrorKind::NotFound, "data dir"))?,
                path,
            )?,
        };

        Ok(Res { kind, path })
    }
}

impl Res {
    fn custom(path: &mut PathBuf, file: &str) -> Result<String> {
        // Creating the directory first
        path.push("vidify");
        if !path.exists() {
            create_dir(&path)?;
        }

        // And then the file
        path.push(file);
        if !path.exists() {
            File::create(&path)?;
        }

        Ok(path.to_string_lossy().into_owned())
    }
}

impl Deref for Res {
    type Target = str;

    fn deref(&self) -> &Self::Target {
        &self.path
    }
}
