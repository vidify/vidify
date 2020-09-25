//! This module contains classes for different kinds of resources. These are
//! specially helpful to make sure the paths that point to them are intialized.
//!
//! Note: a resource is considered a file, not a directory.

use crate::error::Result;

use std::io;
use std::fs;
use std::path::PathBuf;

use pyo3::prelude::*;

#[pymodule]
fn res(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<CustomRes>()?;
    m.add_class::<DataRes>()?;
    m.add_class::<ConfigRes>()?;

    Ok(())
}

pub trait Res {
    fn new(path: &str) -> Result<Self>
        where Self: Sized;

    fn path(&self) -> &str;
}

/// Can be anything, no path is appended to it.
#[pyclass]
pub struct CustomRes {
    path: String,
}

/// Holds persistent data for the user, like `~/.local/share/vidify/2020.log`.
#[pyclass]
pub struct DataRes {
    path: String,
}

/// Holds configuration files, like `~/.config/vidify/config.ini`.
#[pyclass]
pub struct ConfigRes {
    path: String,
}

fn init_path(path: &PathBuf) -> Result<()> {
    if let Some(path) = path.parent() {
        fs::create_dir_all(path)?;
    }
    if let Some(file) = path.file_name() {
        if !path.exists() {
            fs::File::create(file)?;
        }
    }

    Ok(())
}

impl Res for CustomRes {
    fn new(path: &str) -> Result<Self> {
        init_path(&PathBuf::from(path))?;
        Ok(Self { path: path.to_owned() })
    }

    fn path(&self) -> &str {
        &self.path
    }
}

impl Res for ConfigRes {
    fn new(file: &str) -> Result<Self> {
        let mut path = dirs::config_dir().ok_or_else(|| {
            io::Error::new(io::ErrorKind::NotFound, "config dir")
        })?;
        path.push("vidify");
        path.push(file);
        init_path(&path)?;

        Ok(Self { path: path.to_string_lossy().into_owned() })
    }

    fn path(&self) -> &str {
        &self.path
    }
}

impl Res for DataRes {
    fn new(file: &str) -> Result<Self> {
        let mut path = dirs::data_dir().ok_or_else(|| {
            io::Error::new(io::ErrorKind::NotFound, "data dir")
        })?;
        path.push("vidify");
        path.push(file);
        init_path(&path)?;

        Ok(Self { path: path.to_string_lossy().into_owned() })
    }

    fn path(&self) -> &str {
        &self.path
    }
}
