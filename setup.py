from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound, get_distribution
from sys import platform


def is_installed(pkgname: str) -> bool:
    try:
        get_distribution(pkgname)
        return True
    except DistributionNotFound:
        return False


# Get version inside vidify/version.py without importing the package
exec(compile(open('vidify/version.py').read(),
             'vidify/version.py', 'exec'))

install_requires = [
    # Base package
    'QtPy==1.9',
    'lyricwikia==0.1',
    'youtube-dl',
    'appdirs==1.4.4',
    'qdarkstyle==2.8',
    # Fixes for older Python versions
    'dataclasses; python_version<"3.7"',
    # APIs and players
    'tekore==3.*',
    'zeroconf==0.28',
    'pydbus==0.6; platform_system=="Linux"',
    'SwSpotify==1.2; platform_system=="Windows" or platform_system=="Darwin"'
]

# If PySide2 is installed and PyQt5 is not, append PySide2 to dependencies
if is_installed('PySide2') and not is_installed('PyQt5'):
    install_requires.append('PySide2==5.15')
# If PySide2 is not installed, or if both PyQt5 and PySide2 are installed
# Use QtPy's default: PyQt5
else:
    install_requires.append('PyQt5==5.15')

extras_require = {
    "dev": [
        "flake8",
        "black",
        "isort",
        "pyinstaller",
    ]
}

# The desktop entry and the icon will be added to Linux systems.
if platform.startswith("linux"):
    data_files = [
        ("share/applications", ["dev/vidify.desktop"]),
        ("share/pixmaps", ["dev/vidify.svg"]),
    ]
else:
    data_files = []

setup(
    # Basic program information
    name='vidify',
    version=__version__,
    description='Watch music videos in real-time for the songs playing on your device',
    url='https://vidify.org/',
    python_requires='>=3.6',
    license='LGPL',

    # Authors
    author='Mario O.M.',
    author_email='marioortizmanero@gmail.com',
    maintainer='Mario O.M.',
    maintainer_email='marioortizmanero@gmail.com',

    # Metadata for PyPi
    long_description="Read more at https://github.com/vidify/vidify",
    long_description_content_type='text/markdown',
    keywords='spotify music video player videos lyrics linux windows macos',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    # Metadata for the installation
    extras_require=extras_require,
    install_requires=install_requires,
    data_files=data_files,
    packages=find_packages(exclude=('tests*', 'dev*')),
    entry_points={'console_scripts': ['vidify = vidify.__main__:main']},
)
