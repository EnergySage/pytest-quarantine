import codecs
import os

from setuptools import setup


def read(fname):
    """Return the contents of a file in the current directory."""
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-quarantine",
    version="0.1.0.dev2",
    author="Brian Rutledge",
    author_email="bhrutledge@gmail.com",
    maintainer="Brian Rutledge",
    maintainer_email="bhrutledge@gmail.com",
    license="MIT",
    url="https://github.com/bhrutledge/pytest-quarantine",
    description="A plugin for pytest to manage expected test failures",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    py_modules=["pytest_quarantine"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=["pytest>=4.6"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"pytest11": ["quarantine = pytest_quarantine"]},
)
