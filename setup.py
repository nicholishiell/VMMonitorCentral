#!/usr/bin/env python3

from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vm-monitor-central",
    version="0.1.0",
    author="Nicholi Shiell",
    author_email="nickshiell@cunet.carleton.ca",
    description="The central hub for the VM monitoring tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicholishiell/VMonCentral",
    project_urls={
        "Bug Tracker": "https://github.com/nicholishiell/VMonCentral/issues",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "rcsdb",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "vm-monitor-central=vm_monitor_central:main",
        ],
    },
    include_package_data=True,
    package_data={
        "vm_monitor_central": ["*.yaml", "*.yml"],
    },
    zip_safe=False,
    keywords="vm monitoring system administration asyncio",
)