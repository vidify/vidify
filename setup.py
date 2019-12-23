from setuptools import setup, find_packages


# Get version inside spotivids/version.py without importing the package
exec(compile(open('spotivids/version.py').read(),
             'spotivids/version.py', 'exec'))

setup(
    name='spotivids',
    version=__version__,
    packages=['spotivids'],
    description='Watch music videos for the songs playing on your computer',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/marioortizmanero/spotivids',
    license='LGPL',

    author='Mario O.M.',
    author_email='marioortizmanero@gmail.com',
    maintainer='Mario O.M.',
    maintainer_email='marioortizmanero@gmail.com',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='spotify music video videos lyrics spotivids',
    python_requires='>=3.7',
    install_requires=[
        'PySide2',
        'youtube-dl',
        'python-vlc',
        'appdirs',
        'lyricwikia',
        'spotipy>=3.0'
        'pydbus; platform_system=="Linux"',
        'SwSpotify>=1.1.1; platform_system=="Windows" or platform_system=="Darwin"'
    ],
    extras_require={
        'dev': [
            'flake8'
        ],
        'mpv': [
            'python-mpv'
        ]
    },
    entry_points={
        'console_scripts': ['spotivids = spotivids.__main__:main']
    }
)
