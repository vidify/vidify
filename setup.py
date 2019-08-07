from setuptools import setup, find_packages

setup(
    name='spotify-videos',
    version='1.5',
    packages=find_packages(),
    description='Simple tool to show Youtube music videos and lyrics for the playing Spotify songs',
    url='https://github.com/marioortizmanero/spotify-music-videos',
    license='MIT',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='Mario O.M.',
    author_email='marioortizmanero@gmail.com',
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
    install_requires=[
        'youtube-dl',
        'python-vlc',
        'lyricwikia',
        'dbus-python',
        'requests>=2.3.0', # spotipy
        'six>=1.10.0' #spotipy
    ],
    entry_points={
        'console_scripts' : [ 'spotify-videos = spotify_videos.spotify_videos:main' ]
    }
)
