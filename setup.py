"""
Setup script for NightShift-lDownloader
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nightshift-ldownloader",
    version="1.0.0",
    author="Yulong-Cauli",
    description="A time-window based intelligent download manager optimized for nighttime downloads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yulong-Cauli/NightShift-lDownloader",
    py_modules=["download_manager", "cli"],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nightshift=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="download-manager video-downloader telegram youtube twitter time-window",
)
