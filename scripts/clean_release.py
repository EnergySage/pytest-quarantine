import sys
from pathlib import Path
from shutil import rmtree


def main():
    """Remove files created by setup.py."""
    root = Path(__file__).parents[1].resolve()

    for dirname in ["build", "dist"]:
        rmtree(root / dirname, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
