mod error;

use std::time::Duration;

use crate::error::{Error, Result};

use cpal::traits::*;
// use cpal::{OutputCallbackInfo, StreamError};

#[derive(Default, Debug, Clone)]
pub struct Audiosync {}

impl Audiosync {
    pub fn new() -> Self {
        Audiosync {}
    }

    pub fn setup(&self) -> Result<()> {
        Ok(())
    }

    pub fn run(self) -> Result<Duration> {
        let host = cpal::default_host();
        log::info!("Host: {:?}", host.id());

        let device = host.default_output_device().ok_or(Error::NoOutputDevice)?;
        let config = device.default_output_config().unwrap().config();
        log::info!("Device config: {:#?}", config);

        // device.build_output_stream(&config, |data, info| {

        // }, |err| {});

        Ok(Duration::from_millis(0))
    }

    // fn data_callback(&self, data: &mut [f32], info: &OutputCallbackInfo) {}

    // fn error_callback(&self, err: StreamError) {}
}
