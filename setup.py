from setuptools import setup, find_packages


# Get version inside spotivids/version.py without importing the package
exec(compile(open('spotivids/version.py').read(),
             'spotivids/version.py', 'exec'))

setup(
    name='spotivids',
    version=__version__,
    packages=find_packages(),
    description='Watch music videos and lyrics for the playing Spotify songs',
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
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='spotify music video videos lyrics spotivids',
    python_requires='>=3.7',
    install_requires=[
        'youtube-dl',
        'python-vlc',
        'lyricwikia',
        'spotipy',
        'PySide2',
        'pydbus; platform_system=="Linux"',
        'SwSpotify; platform_system=="Windows" or platform_system=="Darwin"'
    ],
    extras_require={
        'mpv': [
            'python-mpv'
        ],
        'dev': [
            'flake8'
        ]
    },
    entry_points={
        'console_scripts': ['spotivids = spotivids.__main__:main']
    }
)
