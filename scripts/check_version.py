import sys

from setuptools_scm import get_version

version = get_version()
print("Version: " + version)

if "+" in version:
    sys.exit(
        "ERROR: Invalid version. "
        "Make sure the working tree is clean, then tag a new version."
    )
