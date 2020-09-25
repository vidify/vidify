use audiosync::Audiosync;

fn main() {
    env_logger::init();

    let audiosync = Audiosync::new();

    audiosync.setup().expect("Failed to set up audiosync");
    audiosync.run().expect("Failed to run algorithm");
}
