#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("No output device found")]
    NoOutputDevice,
}

pub type Result<T> = std::result::Result<T, Error>;
