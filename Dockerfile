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
    libfftw3-dev \
    libgirepository1.0-dev \
    libmpv-dev \
    libnss3 \
    libpulse-dev \
    libvlc-dev \
    pulseaudio \
    vlc \
    xvfb \
    zip \
 && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY dev/build_requires.txt dev/
RUN pip install -r dev/build_requires.txt

# The app is ready to be installed
COPY . .
RUN pip install . --no-deps

CMD sh dev/run-tests-docker.sh
