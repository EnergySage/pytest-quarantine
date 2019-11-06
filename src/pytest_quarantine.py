from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import pytest


# TODO: Guarantee this is opened from pytest's root dir
# (to allow running pytest in a subdirectory)
DEFAULT_QUARANTINE = "quarantine.txt"


class SaveQuarantinePlugin(object):
    """Save a list of failing tests to be marked as xfail on future test runs."""

    def __init__(self, config):
        self.save_quarantine = config.getoption("save_quarantine")
        self.nodeids = set()

    def pytest_report_header(self, config):
        """Display configuration at runtime."""
        if not self.save_quarantine:
            return None
        return "{}: {}".format("save_quarantine", self.save_quarantine)

    def pytest_runtest_logreport(self, report):
        """Save the ID of a failed test to the quarantine."""
        if not report.passed:
            self.nodeids.add(report.nodeid)

    def pytest_sessionfinish(self, session):
        """Write the ID's of quarantined tests to a file."""
        if not (self.save_quarantine and self.nodeids):
            return

        with open(self.save_quarantine, "w") as f:
            f.writelines(nodeid + "\n" for nodeid in sorted(self.nodeids))


class QuarantinePlugin(object):
    """Mark a list of tests in a file as xfail."""

    def __init__(self, config):
        self.quarantine = config.getoption("quarantine")
        self.nodeids = set()

    def pytest_report_header(self, config):
        """Display configuration at runtime."""
        if not self.quarantine:
            return None
        return "{}: {}".format("quarantine", self.quarantine)

    def pytest_runtestloop(self, session):
        """Read the ID's of quarantined tests from a file."""
        if not self.quarantine:
            return

        try:
            with open(self.quarantine) as f:
                self.nodeids = {nodeid.strip() for nodeid in f}
        except IOError:
            # TODO: Would it be better to warn or abort?
            pass

    def pytest_runtest_setup(self, item):
        """Mark a test as `xfail` if its ID is in the quarantine."""
        if self.quarantine and item.nodeid in self.nodeids:
            item.add_marker(pytest.mark.xfail(reason="Quarantined"))


def pytest_configure(config):
    """Register the plugin functionality."""
    # TODO: Only register when the options are present?
    # It could remove the guard conditionals in the classes.
    config.pluginmanager.register(
        SaveQuarantinePlugin(config), "save_quarantine_plugin"
    )
    config.pluginmanager.register(QuarantinePlugin(config), "quarantine_plugin")


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
