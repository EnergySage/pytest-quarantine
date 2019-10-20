import sys

from setuptools_scm import get_version


def main():
    """Validate the package version for PyPI.

    If the version contains a local identifier, return an error message suitable for
    sys.exit. Otherwise, return None.

    See also:
    https://github.com/pypa/setuptools_scm/issues/365
    https://github.com/pypa/twine/issues/430
    https://www.python.org/dev/peps/pep-0440/#local-version-identifiers

    """
    version = get_version()
    print("Version: " + version)

    if "+" in version:
        return (
            "ERROR: Invalid version. "
            "Make sure the working tree is clean, then tag a new version."
        )


if __name__ == "__main__":
    sys.exit(main())
