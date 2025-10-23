#!/usr/bin/env python3
"""
Setup configuration for AutoPassAd.
This file enables pip installation and creates a console script entry point.

Developed with assistance from aider.chat.
"""

from setuptools import setup
import os

# Read the contents of README file for long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements from requirements.txt
# This ensures setup.py and requirements.txt stay in sync
with open(os.path.join(this_directory, "requirements.txt"), encoding="utf-8") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="autopassad",
    version="0.1.0",
    description='Automatically detect "continue" text on screen and simulate mouse clicks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="fPHeQk7",
    url="https://github.com/thiswillbeyourgithub/autopassad",
    license="GPL-v3",
    # Use py_modules since this is a single-file module, not a package
    py_modules=["autopassad"],
    python_requires=">=3.7",
    install_requires=requirements,
    # EasyOCR is optional - provides better accuracy but not required
    # Install with: pip install autopassad[easyocr]
    extras_require={
        "easyocr": ["easyocr"],
    },
    # Create console script entry point for easy command-line access
    # After installation, users can run: autopassad --help
    entry_points={
        "console_scripts": [
            "autopassad=autopassad:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    keywords="ocr automation mouse click screenshot tesseract easyocr",
)
