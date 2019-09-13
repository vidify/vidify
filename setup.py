from setuptools import setup, find_packages
import platform


dependencies = [
    'youtube-dl',
    'python-vlc',
    'lyricwikia',
    'spotipy'  # TODO
]

# DBus is only needed on Linux
if platform.system() == 'Linux':
    dependencies.append('pydbus')


# Get version inside spotify_videos/version.py without importing the package
exec(compile(open('spotify_videos/version.py').read(),
             'spotify_videos/version.py', 'exec'))

setup(
    name='spotify-videos',
    version=__version__,
    packages=find_packages(),
    description='Simple tool to show Youtube music videos and lyrics',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/marioortizmanero/spotify-music-videos',
    license='MIT',

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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='spotify music video videos lyrics',
    python_requires='>=3.6',
    install_requires=dependencies,
    extras_require={
        'mpv': [
            'python-mpv'
        ],
        'dev': [
            'flake8'
        ]
    },
    entry_points={
        'console_scripts': ['spotify-videos = spotify_videos.__main__:main']
    }
)
