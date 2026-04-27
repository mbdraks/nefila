from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="nefila",
    packages=find_packages(),
    version="0.0.5",
    license="GPL-3",
    description="Nefila is an elegant and simple Fortinet Security Fabric library for Python.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Michel Barbosa",
    author_email="nefila@deadpackets.io",
    url="https://github.com/mbdraks/nefila",
    download_url="https://github.com/mbdraks/nefila/archive/v0.0.4.tar.gz",
    keywords=["fortinet", "fortigate", "security fabric"],
    install_requires=["requests", "requests[security]"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.7",
    ],
)
