# Multipurpose Dockerfile for tests and building. It installs every single
# Vidify dependency, even the optionals.
# It uses xvfb to run the Qt tests without an actual X server running.

ARG python_version=3.6
FROM python:${python_version}-buster
WORKDIR /vidify/
# Needed to install programs without interaction
ENV DEBIAN_FRONTEND=noninteractive
# Continuous integration indicator (some tests will be skipped)
ENV CI=true

# Apt build dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gir1.2-gtk-3.0 \
    libasound2-dev \
    libdbus-1-dev \
    libfftw3-dev \
    libgirepository1.0-dev \
    libmpv-dev \
    libnss3 \
    libpango1.0-dev \
    libpulse-dev \
    p7zip-full \
    pulseaudio \
    xvfb \
    zip \
 && rm -rf /var/lib/apt/lists/*

# Installing stable Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="${HOME:-/root}/.cargo/bin:$PATH"
RUN rustup default stable

# Installing Python dependencies
RUN pip install -U pip
COPY dev/build_requires.txt dev/
RUN pip install -r dev/build_requires.txt

# Installing the app itself
COPY . .
RUN pip install ".[dev]" --verbose

CMD sh dev/run-python-tests.sh
