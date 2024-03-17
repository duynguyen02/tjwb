from setuptools import find_packages, setup
from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tjwb',
    packages=find_packages(include=['tjwb']),
    version='1.0.0',
    description='Python library used to calculate reservoir water balance.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='DuyNguyen02',
    install_requires=[
        "pandas"
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ]
)