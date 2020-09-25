# Contributing to Vidify
Any contributions to Vidify are welcome!

There should always be lots of [open issues](https://github.com/vidify/vidify/issues) in the GitHub repo. The easiest ones for newcomers are those tagged with ["good first issue"](https://github.com/vidify/vidify/labels/good%20first%20issue), but you can still try to tackle others. If you need help, leave a comment and a maintainer will try to explain what needs to be done to do in steps. When you open a PR with the implementation, ask for a review to get some feedback on your work.

It's strongly recommended to join [the official Discord server](https://discord.gg/yfJSyPv) for discussion and help when developing.

You can run the module locally with `python -m vidify`, after running `python setup.py develop`. The first command will run the Python module, but you need the second one to compile the Rust parts of Vidify ([make sure you have Rust installed in your system](https://www.rust-lang.org/tools/install)). You will also need all the required Python dependencies installed with `pip install -e .`.

## Project organization
Vidify combines both Rust and Python, the former for core and performance-focused parts, and the latter for the rest. Here's a brief description of the directories in this repository:

- `src`: source code
    + `audiosync`: the audiosync feature, written in Rust
    + `core`: some parts of Vidify written in Rust
    + `vidify`: main source code for both the logic and GUI of Vidify, in Python
- `res`: resources Vidify uses, like fonts, icons, images...
- `dev`: some scripts and tools needed for developer tasks, like building
- `tests`: both Rust and Python tests. See the [Tests](#tests) section for more
- `images`: some images used for the `README.md` and such

## Style
Vidify tries to follow a consistent style for both Python and Rust by using automatic formatting tools:
* `cargo fmt` as the Rust formatter, and `cargo clippy` as the linter.
* `black`, `isort` for formatting, and `flake8` for linting. Simply run them with `python -m <module>` at the root of the repo.

## Building
See the [BUILDING.md](./BUILDING.md) file for more information about building Vidify into binaries.

## Tests
This project uses `unittest` for testing with Python. Run them with `python -m unittest`. You'll need all the extra dependencies installed for this to work.

Rust tests can be ran with `cargo test`.
