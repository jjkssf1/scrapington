#!/usr/bin/env python3
"""
Setup script for Scrapington - Universal GeoJSON Scraper
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="scrapington",
    version="1.0.0",
    description="Universal GeoJSON scraper for ArcGIS Feature Services",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jjkssf1/scrapington",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "scrapington=universal_scraper:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="gis geojson arcgis scraper data-extraction spatial",
    project_urls={
        "Bug Reports": "https://github.com/jjkssf1/scrapington/issues",
        "Source": "https://github.com/jjkssf1/scrapington",
        "Documentation": "https://github.com/jjkssf1/scrapington#readme",
    },
)
