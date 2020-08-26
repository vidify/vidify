from os.path import join, dirname, abspath
from setuptools import setup, find_packages
from setuptools_rust import RustExtension, Binding
from pkg_resources import DistributionNotFound, get_distribution
from sys import platform


def is_installed(pkgname: str) -> bool:
    try:
        get_distribution(pkgname)
        return True
    except DistributionNotFound:
        return False


# The version should be the same as the one in `Cargo.toml`.
def get_version():
    cargo_dir = join(dirname(abspath(__file__)), 'Cargo.toml')
    with open(cargo_dir, 'r') as f:
        for line in f:
            split = line.split()
            if split[0] == 'version':
                return split[2][:-1][1:]

    raise "Couldn't find `Cargo.toml` version"


version = get_version()

install_deps = [
    # Base package
    'QtPy',
    'lyricwikia',
    'youtube-dl',
    'qdarkstyle',
    'dataclasses; python_version<"3.7"',
    'vidify_audiosync',
    # APIs and players
    'tekore<3.0',
    'zeroconf',
    'pydbus; platform_system=="Linux"',
    'SwSpotify>=1.1.1; platform_system=="Windows"'
    ' or platform_system=="Darwin"'
]

# If PySide2 is installed and PyQt5 is not, append PySide2 to dependencies
if is_installed('PySide2') and not is_installed('PyQt5'):
    install_deps.append('PySide2')
# If PySide2 is not installed, or if both PyQt5 and PySide2 are installed
# Use QtPy's default: PyQt5
else:
    install_deps.append('PyQt5')

extras_require = {
    'dev': [
        'flake8',
        'pyinstaller'
    ]
}

setup_requires = [
    # Rust extensions will be included with `setuptools-rust`.
    "setuptools-rust"
]

# The Rust extensions will share the same `vidify` namespace as the Python
# module.
rust_ext_conf = {
    'path': 'Cargo.toml',
    'binding': Binding.PyO3,
    'debug': False
}
rust_extensions = [
    RustExtension(
        "vidify.config",
        **rust_ext_conf
    ),
    # RustExtension(
    #     "vidify.audiosync",
    #     **rust_ext_conf
    # )
]

packages = find_packages(exclude=('tests*', 'dev*'))

# The desktop entry and the icon will be added to Linux systems.
if platform.startswith('linux'):
    datafiles = [('share/applications', ['dev/vidify.desktop']),
                 ('share/pixmaps', ['dev/vidify.svg'])]
else:
    datafiles = []

setup(
    # Metadata for publishing
    name='vidify',
    version=version,
    packages=packages,
    description='Watch music videos in real-time for the songs playing on'
                ' your device',
    url='https://vidify.org/',
    license='LGPL',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'License :: OSI Approved :: GNU Lesser General Public License v3'
        ' (LGPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='spotify music video player videos lyrics linux windows macos',

    # Data included
    package_dir={"": "src/vidify"},
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    package_data={'vidify': ['gui/res/*',
                             'gui/res/*/*',
                             'gui/res/*/*/*']},
    data_files=datafiles,

    # Authors
    author='Mario O.M.',
    author_email='marioortizmanero@gmail.com',
    maintainer='Mario O.M.',
    maintainer_email='marioortizmanero@gmail.com',

    # Metadata for the installation
    python_requires='>=3.6',
    install_requires=install_deps,
    extras_require=extras_require,
    entry_points={
        'console_scripts': ['vidify = vidify.__main__:main']
    },
    rust_extensions=rust_extensions,
    setup_requires=setup_requires,
    zip_safe=False,  # Rust extensions are not zip safe
)
