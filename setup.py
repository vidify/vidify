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

install_deps = [
    'QtPy',
    'qdarkstyle',
    'youtube-dl',
    'python-vlc',
    'appdirs',
    'lyricwikia',
    'tekore',
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
    install_deps.append('PyQtWebEngine')

if platform.startswith('linux'):
    datafiles = [('share/applications', ['dev/vidify.desktop']),
                 ('share/pixmaps', ['dev/vidify.svg'])]
else:
    datafiles = []

setup(
    name='vidify',
    version=__version__,
    packages=find_packages(exclude=('tests*', 'dev*')),
    description='Watch music videos for the songs playing on your device',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vidify/vidify',
    license='LGPL',

    package_data={'vidify': ['gui/res/*',
                             'gui/res/*/*',
                             'gui/res/*/*/*']},

    data_files=datafiles,

    author='Mario O.M.',
    author_email='marioortizmanero@gmail.com',
    maintainer='Mario O.M.',
    maintainer_email='marioortizmanero@gmail.com',

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
    python_requires='>=3.6',
    install_requires=install_deps,
    extras_require={
        'dev': [
            'flake8'
        ],
        'audiosync': [
            'vidify-audiosync'
        ],
        'mpv': [
            'python-mpv'
        ]
    },
    entry_points={
        'console_scripts': ['vidify = vidify.__main__:main']
    }
)
