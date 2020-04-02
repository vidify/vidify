# Multipurpose Dockerfile for tests and building. It installs every single
# Vidify dependency, even the optionals.
# I still haven't managed to get it working for tests because Qt requires
# an open X server, though.

FROM python:3.6
WORKDIR /vidify/
# Needed to install programs without interaction
ENV DEBIAN_FRONTEND=noninteractive

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
    libpulse-dev \
    libvlc-dev \
    mpv \
    pulseaudio \
    python-gobject \
    vlc \
    zip \
 && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY dev/linux_requires.txt .
RUN pip install -r linux_requires.txt

# The app is ready to be installed
COPY . .
RUN pip install . --no-deps
