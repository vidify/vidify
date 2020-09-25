use audiosync::Audiosync;
use simple_logger::SimpleLogger;

fn main() {
    SimpleLogger::new().init().unwrap();

    let audiosync = Audiosync::new();

    audiosync.setup().expect("Failed to set up audiosync");
    audiosync.run().expect("Failed to run algorithm");
}
