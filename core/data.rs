use crate::error::Result;

use std::fs::{create_dir, File};
use std::ops::Deref;
use std::path::PathBuf;

use dirs::*;

/// What kind of resource it is, to determine where it should be stored. The
/// custom type holds the full path, the rest of them only contain the file
/// name, which will be appended to a predetermined directory.
pub enum ResKind {
    Custom,
    Config,
    Data,
}

/// The actual struct with the functionalities required to initialize the
/// resource's path and access to them.
pub struct Res {
    pub kind: ResKind,
    pub path: String,
}

impl Res {
    pub fn new(kind: ResKind, path: &str) -> Result<Res> {
        use std::io::{Error, ErrorKind};
        use ResKind::*;

        let path = match kind {
            Custom => path.to_string(),
            Config => Res::custom(
                &mut config_dir()
                    .ok_or(Error::new(ErrorKind::NotFound, "config dir"))?,
                path,
            )?,
            Data => Res::custom(
                &mut data_dir()
                    .ok_or(Error::new(ErrorKind::NotFound, "data dir"))?,
                path,
            )?,
        };

        Ok(Res {
            kind,
            path,
        })
    }

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
