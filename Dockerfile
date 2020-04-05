# Multipurpose Dockerfile for tests and building. It installs every single
# Vidify dependency, even the optionals.
# It uses xvfb to run the Qt tests without an actual X server running.

FROM python:3.6
WORKDIR /vidify/
# Needed to install programs without interaction
ENV DEBIAN_FRONTEND=noninteractive
# Continuous integration indicator (some tests will be skipped)
ENV CI=true

# Apt build dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gir1.2-gtk-3.0 \
    libcairo2-dev \
    libdbus-glib-1-dev \
    libfftw3-dev \
    libgirepository1.0-dev \
    libglib2.0-dev \
    libmpv-dev \
    libnss3 \
    libpulse-dev \
    libvlc-dev \
    mpv \
    pulseaudio \
    python-gobject \
    vlc \
    xvfb \
    zip \
 && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY dev/linux_requires.txt .
RUN pip install -r linux_requires.txt

# The app is ready to be installed
COPY . .
RUN pip install . --no-deps

RUN chmod a+x dev/run-tests-docker.sh
CMD dev/run-tests-docker.sh
