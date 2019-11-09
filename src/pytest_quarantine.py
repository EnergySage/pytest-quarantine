from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import pytest


# TODO: Guarantee this is opened from pytest's root dir
# (to allow running pytest in a subdirectory)
DEFAULT_QUARANTINE = "quarantine.txt"


def _quarantine_size(nodeids):
    num_tests = len(nodeids)
    return "{} test{}".format(num_tests, "" if num_tests == 1 else "s")


class SaveQuarantinePlugin(object):
    """Save the list of failing tests to a quarantine file."""

    def __init__(self, quarantine_path):
        self.quarantine_path = quarantine_path
        self.nodeids = set()

    def pytest_runtest_logreport(self, report):
        """Save the ID of a failed test to the quarantine."""
        if not report.passed:
            self.nodeids.add(report.nodeid)

    def pytest_terminal_summary(self, terminalreporter):
        """Display size of quarantine after running tests."""
        if not self.nodeids:
            return

        terminalreporter.write_sep(
            "-",
            "{} saved to {}".format(
                _quarantine_size(self.nodeids), self.quarantine_path
            ),
        )

    def pytest_sessionfinish(self, session):
        """Write the ID's of quarantined tests to a file."""
        if not self.nodeids:
            return

        with open(self.quarantine_path, "w") as f:
            f.writelines(nodeid + "\n" for nodeid in sorted(self.nodeids))


class QuarantinePlugin(object):
    """Mark each test listed in a quarantine file as xfail."""

    def __init__(self, quarantine_path):
        self.quarantine_path = quarantine_path
        self.nodeids = set()

    def pytest_sessionstart(self, session):
        """Read test ID's from a file into the quarantine."""
        try:
            with open(self.quarantine_path) as f:
                self.nodeids = {nodeid.strip() for nodeid in f}
        except IOError as exc:
            raise pytest.UsageError("Could not load quarantine: " + str(exc))

    def pytest_report_collectionfinish(self):
        """Display size of quarantine before running tests."""
        return "quarantine: {} in {}".format(
            _quarantine_size(self.nodeids), self.quarantine_path
        )

    def pytest_runtest_setup(self, item):
        """Mark a test as xfail if its ID is in the quarantine."""
        if item.nodeid in self.nodeids:
            item.add_marker(pytest.mark.xfail(reason="Quarantined"))


def pytest_configure(config):
    """Register the plugin functionality."""
    save_quarantine_path = config.getoption("save_quarantine")
    if save_quarantine_path:
        config.pluginmanager.register(
            SaveQuarantinePlugin(save_quarantine_path), "save_quarantine_plugin"
        )

    quarantine_path = config.getoption("quarantine")
    if quarantine_path:
        config.pluginmanager.register(
            QuarantinePlugin(quarantine_path), "quarantine_plugin"
        )


def pytest_addoption(parser):
    """Add command line options to the 'quarantine' group."""
    group = parser.getgroup("quarantine")

    group.addoption(
        "--save-quarantine",
        nargs="?",
        const=DEFAULT_QUARANTINE,
        metavar="PATH",
        help="Write failing tests to %(metavar)s (default: %(const)s)",
    )

    group.addoption(
        "--quarantine",
        nargs="?",
        const=DEFAULT_QUARANTINE,
        metavar="PATH",
        help="Mark tests listed in %(metavar)s with `xfail` (default: %(const)s)",
    )
