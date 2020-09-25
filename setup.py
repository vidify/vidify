from os.path import abspath, dirname, join
from sys import platform

from pkg_resources import DistributionNotFound, get_distribution
from setuptools import find_packages, setup
from setuptools_rust import Binding, RustExtension


def is_installed(pkgname: str) -> bool:
    try:
        get_distribution(pkgname)
        return True
    except DistributionNotFound:
        return False


# The version should be the same as the one in `Cargo.toml`.
def get_version():
    cargo_dir = join(dirname(abspath(__file__)), "src", "core", "Cargo.toml")
    with open(cargo_dir, "r") as f:
        for line in f:
            split = line.split()
            if len(split) > 0 and split[0] == "version":
                return split[2][:-1][1:]

    raise Exception("Couldn't find `Cargo.toml` version")


version = get_version()

install_requires = [
    # Base package
    "QtPy==1.9",
    "lyricwikia==0.1",
    "youtube-dl",
    "qdarkstyle==2.8",
    'dataclasses; python_version<"3.7"',
    # APIs and players
    "tekore==3",
    "flask==1.1",
    "zeroconf==0.28",
    'pydbus==0.6; platform_system=="Linux"',
    'SwSpotify==1.2; platform_system=="Windows" or platform_system=="Darwin"',
]

# If PySide2 is installed and PyQt5 is not, append PySide2 to dependencies
if is_installed("PySide2") and not is_installed("PyQt5"):
    install_requires.append("PySide2==5.15")
# If PySide2 is not installed, or if both PyQt5 and PySide2 are installed
# Use QtPy's default: PyQt5
else:
    install_requires.append("PyQt5==5.15")

extras_require = {
    "dev": [
        "flake8",
        "black",
        "isort",
        "pyinstaller",
    ]
}

# The Rust extensions will share the same `vidify` namespace as the Python
# module.
rust_ext_conf = {"binding": Binding.PyO3, "debug": False}
rust_extensions = [
    RustExtension("vidify.core", path="src/core/Cargo.toml", **rust_ext_conf),
    # RustExtension(
    #     "vidify._audiosync",
    #     path="src/audiosync/Cargo.toml",
    #     **rust_ext_conf
    # ),
]

packages = find_packages(exclude=("tests*", "dev*"))

# The desktop entry and the icon will be added to Linux systems.
if platform.startswith("linux"):
    datafiles = [
        ("share/applications", ["dev/vidify.desktop"]),
        ("share/pixmaps", ["dev/vidify.svg"]),
    ]
else:
    datafiles = []

setup(
    # Metadata for publishing
    name="vidify",
    version=version,
    packages=packages,
    description="Watch music videos in real-time for the songs playing on"
    " your device",
    url="https://vidify.org/",
    license="GPL-3.0+",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="spotify music video player videos lyrics linux windows macos",
    # Data included
    package_dir={"": "src"},
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    data_files=datafiles,
    # Authors
    author="Mario Ortiz Manero",
    author_email="marioortizmanero@gmail.com",
    maintainer="Mario Ortiz Manero",
    maintainer_email="marioortizmanero@gmail.com",
    # Metadata for the installation
    python_requires=">=3.6",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={"console_scripts": ["vidify = vidify.__main__:main"]},
    rust_extensions=rust_extensions,
    zip_safe=False,  # Rust extensions are not zip safe
)
