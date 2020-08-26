#!/usr/bin/env python3

"""
This script builds Vidify into a binary for the supported Operating Systems.
Requires:
    * 7zip (system, `7z` in path)
    * libmpv (system, Linux and Darwin)
    * pyinstaller
"""

from typing import Tuple
import PyInstaller.__main__ as pyinstaller
import logging
import os
import platform
import shutil
import subprocess
import urllib.request

MPV_DOWNLOAD_WINDOWS = "https://downloads.sourceforge.net/project/mpv-player-windows/libmpv/mpv-dev-x86_64-20200405-git-c5f8ec7.7z?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fmpv-player-windows%2Ffiles%2Flibmpv%2Fmpv-dev-x86_64-20200405-git-c5f8ec7.7z%2Fdownload&ts=1586353127"

IGNORED_FILES = [".git", ".venv", "target"]

ALL_OS = ["Linux", "Windows", "Darwin"]


def download_file(uri: str, name: str) -> None:
    with open(name, "wb") as output_file:
        with urllib.request.urlopen(name) as input_file:
            output_file.write(input_file.read())


# This function is used in shutil.copytree to ignore specific files
def get_ignored(path: str, filenames: Tuple[str]) -> None:
    ret = []
    for filename in filenames:
        if os.path.join(path, filename) in IGNORED_FILES:
            ret.append(filename)
    return ret


# Returns a tuple from a dictionary with keys depending on the supported OS.
# See `args_os` below.
def filter_os_args(args: Tuple[str]) -> Tuple[str]:
    args_os = []
    cur_os = platform.system()
    for val, supp_os in args.items():
        if cur_os in supp_os:
            args_os.append(val)

    return args_os


# Making sure the current OS is supported
cur_os = platform.system()
if cur_os not in ALL_OS:
    raise Exception("The {cur_os} Operating System is not supported.")

# Setting up the script
logging.basicConfig(level=logging.DEBUG)

# Everything is copied and built in a temporary directory because this
# script will apply patches to Vidify's source code.
logging.info("Copying data into build directory")
shutil.rmtree("build", ignore_errors=True)
shutil.copytree(".", "build", ignore=get_ignored)

logging.info("Compiling external libraries")
os.chdir("build")
ret = subprocess.run(["python", "setup.py", "develop"])
if ret.returncode != 0:
    logging.error("Compilation failed")
    exit(1)

logging.info("Downloading libraries")
# Downloading mpv so that it can be embed in the binary
if cur_os == "Windows":
    download_file(MPV_DOWNLOAD_WINDOWS, "libmpv.7z")
    subprocess.run(["7z", "e", "-y", "libmpv.7z"])
    if ret.returncode != 0:
        logging.error("Couldn't extract libmpv.7z")
        exit(1)
else:
    ret = subprocess.run(
        ["find", "/", "-name", "libmpv.so", "-print", "-quit"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    path = ret.stdout.decode("utf-8").strip()
    if len(path) == 0:
        logging.error("Couldn't find libmpv.so")
        exit(1)
    shutil.copy(path, ".")

logging.info("Applying pre-build patches")

# PyInstaller args may depend on the Operating System. They are listed as
# dictionaries for simplicity.
logging.info("Running PyInstaller")
args_os = {
    # The basic information
    "--name=vidify": ALL_OS,
    # TODO: may not be necessary
    #  '--add-data=tekore/VERSION:tekore/VERSION': ALL_OS,
    # TODO: may not be necessary
    "--hidden-import=pkg_resources.py2_warn": ALL_OS,
    # External libraries
    f'--add-data={os.path.join("src", "vidify", "config.cpython*")}:.': ALL_OS,
    "--add-data=mpv-1.dll": ["Windows"],
    "--exclude-module=PySide2": ALL_OS,
    os.path.join("src", "vidify", "__main__.py"): ALL_OS,
    os.path.join("src", "vidify", "player", "mpv.py"): ALL_OS,
    os.path.join("src", "vidify", "api", "spotify", "web.py"): ALL_OS,
    os.path.join("src", "vidify", "audiosync.py"): ALL_OS,
    os.path.join("src", "vidify", "api", "mpris.py"): ["Linux"],
    os.path.join("src", "vidify", "api", "spotify", "swspotify.py"): [
        "Windows",
        "Darwin",
    ],
}
args = filter_os_args(args_os)
pyinstaller.run(args)
