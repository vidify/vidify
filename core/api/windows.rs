use crate::api::APIBase;
use crate::config::Config;
use crate::error::Result;

use std::time;

pub struct Windows {}

impl APIBase for Windows {
    fn new(config: &Config, sender: super::Sender) -> Result<Self> {
        Ok(Windows {})
    }

    fn player_name(&self) -> String {
        String::from("Windows Player")
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
