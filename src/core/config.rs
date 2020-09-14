//! TODO: module-level docs

use crate::error::{Error, Result};
use crate::res::{Res, ResKind};

use std::fs::File;
use std::str::FromStr;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use structconf::{clap, StructConf};

#[pymodule]
fn config(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<Config>()?;
    m.add_wrapped(wrap_pyfunction!(init_config))?;
    m.add_wrapped(wrap_pyfunction!(init_logging))?;

    Ok(())
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

    fn from_str(input: &str) -> std::result::Result<Self, Self::Err> {
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
        let mut ret = String::new();
        for (key, val) in &self.values {
            ret.push_str(&format!("{}={};", key, val));
        }

        ret
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
    let path = match args.value_of("config_path") {
        Some(path) => Res::new(ResKind::Custom, path)?,
        None => Res::new(ResKind::Config, "config.ini")?,
    };

    let conf = Config::parse_file(&args, &path)?;
    Ok(conf)
}

#[pyfunction]
pub fn init_logging(config: &Config) {
    use simplelog::{CombinedLogger, Config, LevelFilter, TermLogger, TerminalMode, WriteLogger};

    let file = Res::new(ResKind::Data, "session.log").expect("Couldn't load log file");
    let file: &str = &file;
    CombinedLogger::init(vec![
        TermLogger::new(
            if config.debug {
                LevelFilter::Trace
            } else {
                LevelFilter::Off
            },
            Config::default(),
            TerminalMode::Stderr,
        ),
        WriteLogger::new(
            LevelFilter::Trace,
            Config::default(),
            File::open(file).unwrap(),
        ),
    ])
    .expect("Couldn't load loggers");
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
