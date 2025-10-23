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

# Core dependencies required for basic functionality
# OCR backends (pytesseract and easyocr) are optional - at least one is needed for the tool to work
# Users should install at least one OCR backend via extras_require (see below)
requirements = [
    "Pillow",  # For image capture and processing
    "pynput",  # For mouse control and cursor position
    "rapidfuzz",  # For fuzzy text matching
    "imagehash",  # For duplicate image detection
    "numpy",  # For image processing operations
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
    python_requires=">=3.13",
    install_requires=requirements,
    # At least one OCR backend must be installed for the tool to function
    # pytesseract: Faster, lighter weight, requires tesseract binary to be installed separately
    # easyocr: More accurate, GPU-accelerated, but heavier dependencies
    # Install options:
    #   pip install autopassad[pytesseract]  # Use pytesseract
    #   pip install autopassad[easyocr]      # Use easyocr  
    #   pip install autopassad[all]          # Install both (recommended)
    extras_require={
        "pytesseract": ["pytesseract"],
        "easyocr": ["easyocr"],
        "all": ["pytesseract", "easyocr"],
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
