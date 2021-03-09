//! This crate exposes some utilities common between Rust and Python, mainly
//! some basic logging options and the config class. The latter combines the
//! config file and argument parsing into a single object for ease of use.
//!
//! This is written in Rust mainly to take advantage of the type system and for
//! performance, which makes for example the config file more robust than a
//! solution with Python using reflection.

pub mod error;

use crate::error::{Error, Result};

use std::fs;
use std::io;
use std::path::PathBuf;

use std::fs::File;
use std::str::FromStr;

use dirs_next as dirs;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use simplelog::{CombinedLogger, LevelFilter, TermLogger, TerminalMode, WriteLogger};
use structconf::{clap, StructConf};

/// Public functions for Python, included as `vidify.core`.
#[pymodule]
fn core(_py: Python<'_>, core: &PyModule) -> PyResult<()> {
    core.add_class::<Config>()?;
    core.add_wrapped(wrap_pyfunction!(init_config))?;
    core.add_wrapped(wrap_pyfunction!(init_logging))?;
    core.add_wrapped(wrap_pyfunction!(log))?;
    core.add_wrapped(wrap_pyfunction!(init_custom_res))?;
    core.add_wrapped(wrap_pyfunction!(init_data_res))?;
    core.add_wrapped(wrap_pyfunction!(init_config_res))?;

    Ok(())
}

fn init_path(path: &PathBuf) -> Result<()> {
    // Creating the previous directories
    if let Some(path) = path.parent() {
        fs::create_dir_all(path)?;
    }

    // And also creating the file itself
    if !path.exists() {
        fs::File::create(path)?;
    }

    Ok(())
}

/// The path for the passed file will be initialized, meaning that all the
/// required directories will be created, and the file itself.
#[pyfunction]
pub fn init_custom_res(file: &str) -> Result<String> {
    init_path(&PathBuf::from(file))?;

    Ok(file.to_owned())
}

/// Holds configuration files, like `~/.config/vidify/config.ini`.
/// Its path will be initialized like `init_custom_res`.
#[pyfunction]
pub fn init_config_res(file: &str) -> Result<String> {
    let mut path =
        dirs::config_dir().ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, "config dir"))?;
    path.push("vidify");
    path.push(file);
    init_path(&path)?;

    Ok(path.to_string_lossy().into_owned())
}

/// Holds persistent data for the user, like `~/.local/share/vidify/2020.log`.
/// Its path will be initialized like `init_custom_res`.
#[pyfunction]
pub fn init_data_res(file: &str) -> Result<String> {
    let mut path =
        dirs::data_dir().ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, "data dir"))?;
    path.push("vidify");
    path.push(file);
    init_path(&path)?;

    Ok(path.to_string_lossy().into_owned())
}

/// The generic properties are represented by this struct, which uses the
/// format `key1=val1;key2=val2`. In the future with const generics, the
/// delimiter could be made generic as well. For now, it's `;`.
///
/// This way, the string provided from the config can be parsed only once and
/// at the beginning of the program into an easier to use type.
///
/// It's basically a thin wrapper over a vector, so all its methods can be
/// used after a deref.
#[pyclass]
#[derive(Default, Debug)]
pub struct Properties {
    values: Vec<(String, String)>,
}

impl FromStr for Properties {
    type Err = Error;

    fn from_str(input: &str) -> Result<Self> {
        // An empty value will result in an empty vector to reduce errors.
        if input.len() == 0 {
            return Ok(Self::default());
        }

        // The last character is ignored if it's a delimiter, also to reduce
        // errors.
        let input = input.trim_end_matches(';');
        let err = || {
            Error::ConfigParse(structconf::Error::Parse(
                "Invalid properties: the provided value doesn't match the \
                    format `key1=val1;key2=val2`"
                    .to_string(),
            ))
        };

        let mut values = Vec::new();
        for flag in input.split(';') {
            let mut iter = flag.split('=');
            let key = iter.next().ok_or_else(err)?;
            let val = iter.next().ok_or_else(err)?;
            values.push((key.to_owned(), val.to_owned()));
        }

        Ok(Properties { values })
    }
}

impl ToString for Properties {
    fn to_string(&self) -> String {
        self.values
            .iter()
            .map(|(key, val)| format!("{}={};", key, val))
            .collect()
    }
}

impl std::ops::Deref for Properties {
    type Target = Vec<(String, String)>;

    fn deref(&self) -> &Self::Target {
        &self.values
    }
}

/// The config file saves the app's state and configuration in a config file,
/// wich can be overriden with CLI arguments. If none of them are present for
/// some option, its default value will be used.
#[pyclass]
#[derive(Debug, StructConf)]
pub struct Config {
    #[pyo3(get, set)]
    #[conf(help = "Display debug messages")]
    pub debug: bool,

    /// Custom config file, only available for the argument parser, which
    /// can be obtained by initializing the struct in two steps with
    /// `Config::parse_args`.
    #[pyo3(get, set)]
    #[conf(no_file, help = "The config file path")]
    pub conf_file: Option<String>,

    #[pyo3(get, set)]
    #[conf(
        negated_arg,
        long = "no_lyrics",
        short = "n",
        help = "Do not print lyrics"
    )]
    pub lyrics: bool,

    #[pyo3(get, set)]
    #[conf(help = "The initial window's width")]
    pub width: bool,

    #[pyo3(get, set)]
    #[conf(help = "The initial window's height")]
    pub height: bool,

    #[pyo3(get, set)]
    #[conf(help = "Open the app in fullscreen mode")]
    pub fullscreen: bool,

    #[pyo3(get, set)]
    #[conf(no_short, help = "Activate the dark mode")]
    pub dark_mode: bool,

    #[pyo3(get, set)]
    #[conf(no_short, help = "The window will stay on top of all apps")]
    pub stay_on_top: bool,

    #[pyo3(get, set)]
    #[conf(help = "The source music player used. Read the installation guide \
           for a list with the available APIs")]
    pub api: Option<String>,

    #[pyo3(get, set)]
    #[conf(help = "The output video player. Read the installation guide for \
           a list with the available players")]
    pub player: Option<String>,

    #[pyo3(get, set)]
    #[conf(
        no_short,
        help = "Enable automatic audio synchronization. Read the \
           installation guide for more information. Note: this feature is \
           still in development"
    )]
    pub audiosync: bool,

    #[pyo3(get, set)]
    #[conf(no_short, help = "Manual tweaking value for audiosync in milliseconds")]
    pub audiosync_calibration: i32,

    #[conf(
        no_short,
        help = "Custom properties used when opening mpv, like \
            `msg-level=ao/sndio=no;brightness=50;sub-gray=true`.
            See all of them here: https://mpv.io/manual/master/#options"
    )]
    pub mpv_properties: Properties,

    #[pyo3(get, set)]
    #[conf(
        no_short,
        help = "The client ID for the Spotify Web API. Check the guide to \
           learn how to obtain yours",
        section = "SpotifyWeb"
    )]
    pub client_id: Option<String>,

    #[pyo3(get, set)]
    #[conf(
        no_short,
        help = "The client secret for the Spotify Web API. Check the install \
           guide to learn how to obtain yours",
        section = "SpotifyWeb"
    )]
    pub client_secret: Option<String>,

    #[pyo3(get, set)]
    #[conf(
        no_short,
        help = "The redirect URI used for the Spotify Web API",
        section = "SpotifyWeb",
        default = "String::from(\"http://localhost:8888/callback/\")"
    )]
    pub redirect_uri: String,

    #[pyo3(get, set)]
    #[conf(no_short, no_long, section = "SpotifyWeb")]
    pub refresh_token: Option<String>,
}

/// Initializes the application's configuration structure. The config file
/// will be at the user's default config path, or whichever is specified
/// by `--config-file`.
///
/// NOTE: maybe it should return a `Mutex` or `RwLock`.
#[pyfunction]
pub fn init_config(args: Vec<String>) -> Result<Config> {
    // Author and version pulled at compile time from `Cargo.toml`.
    let app = clap::App::new("vidify")
        .version(clap::crate_version!())
        .author(clap::crate_authors!());
    let args = Config::parse_args_from(app, args);
    let res = match args.value_of("conf_file") {
        Some(path) => init_custom_res(path)?,
        None => init_config_res("config.ini")?,
    };

    let conf = Config::parse_file(&args, &res)?;
    Ok(conf)
}

/// TODO: this shouldn't panic
#[pyfunction]
pub fn init_logging(config: &Config) {
    let res = init_data_res("session.log").expect("Couldn't load log file");
    CombinedLogger::init(vec![
        TermLogger::new(
            if config.debug {
                LevelFilter::Trace
            } else {
                LevelFilter::Off
            },
            simplelog::Config::default(),
            TerminalMode::Stderr,
        ),
        WriteLogger::new(
            LevelFilter::Trace,
            simplelog::Config::default(),
            File::open(&res).unwrap(),
        ),
    ])
    .expect("Couldn't load loggers");
}

/// All logs from Vidify have the 'info' level for now for simplicity.
///
/// This is used instead of Python's native logging module to have a common
/// ground for both Rust and Python logging. Thus, it requires to use f-strings
/// on Python, which aren't recommended in the native module because they will
/// be evaluated even when logging is disabled. In this case, though, logging
/// is always enabled at least for the logging file, so this doesn't matter.
#[pyfunction]
pub fn log(msg: &str) {
    log::info!("{}", msg);
}

#[cfg(test)]
mod test {
    use super::*;

    /// The default value should be equivalent to an empty vector.
    #[test]
    fn test_default_properties() {
        let properties = Properties::default();
        assert_eq!(properties.len(), 0);
    }

    /// An empty string should be equivalent to an empty vector.
    #[test]
    fn test_properties_from_empty_str() {
        let properties = Properties::from_str("").unwrap();
        assert_eq!(properties.len(), 0);
    }

    #[test]
    fn test_properties_from_str_simple() {
        let properties = Properties::from_str("key1=val1").unwrap();
        assert_eq!(
            properties.get(0),
            Some(&("key1".to_string(), "val1".to_string()))
        );
        assert_eq!(properties.get(1), None);
    }

    // Testing the same as before but with a delimiter at the end to make
    // sure it's the same result.
    #[test]
    fn test_properties_from_str_simple_delimiter_end() {
        let properties = Properties::from_str("key1=val1;").unwrap();
        assert_eq!(
            properties.get(0),
            Some(&("key1".to_string(), "val1".to_string()))
        );
        assert_eq!(properties.get(1), None);
    }

    /// Now with multiple keys and values
    #[test]
    fn test_properties_from_str_multiple() {
        let properties = Properties::from_str("key1=val1;key2=val2;key3=val3;").unwrap();
        assert_eq!(
            properties.get(0),
            Some(&("key1".to_string(), "val1".to_string()))
        );
        assert_eq!(
            properties.get(1),
            Some(&("key2".to_string(), "val2".to_string()))
        );
        assert_eq!(
            properties.get(2),
            Some(&("key3".to_string(), "val3".to_string()))
        );
        assert_eq!(properties.get(3), None);
    }

    /// Making sure that not including a '=' fails, for simplicity.
    #[test]
    #[should_panic]
    fn test_properties_from_str_no_equal() {
        Properties::from_str("key1;key2=val2").unwrap();
    }
}
