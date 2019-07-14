from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='spotify-videoclips',
    version='1.0',
    packages=find_packages(include=[
        'src', 'src.*'
    ]),
    description='Simple tool to show Youtube videoclips and lyrics for the playing Spotify songs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/marioortizmanero/spotify-videoclips',
    license='MIT',
    author='Mario O.M.',
    author_email='marioortizmanero@gmail.com',
    classifiers=[
        'Development Status :: 5 - Stable',
        'Intended Audience :: End Users',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='spotify videoclip videoclips video videos lyrics',
    python_requires='>=3.5',
    install_requires=['youtube-dl', 'python-vlc'],
    entry_points={
        'console_scripts' : [ 'spotify-videoclips = src.spotify_videoclips:main' ]
    }
)
