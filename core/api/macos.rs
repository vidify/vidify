use crate::api::APIBase;
use crate::config::Config;
use crate::error::Result;

use std::time;

pub struct MacOS {}

impl APIBase for MacOS {
    fn new(config: &Config, sender: super::Sender) -> Result<Self> {
        Ok(MacOS {})
    }

    fn player_name(&self) -> String {
        String::from("Mac OS")
    }

    fn artist(&self) -> Option<String> {
        None
    }

    fn title(&self) -> Option<String> {
        None
    }

    fn position(&self) -> Option<time::Duration> {
        None
    }

    fn is_playing(&self) -> bool {
        true
    }

    fn event_loop(&mut self) {
        unimplemented!();
    }
}
