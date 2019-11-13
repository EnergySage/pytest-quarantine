"""A plugin for pytest to manage expected test failures.

Saves the list of failing tests, so that they can be automatically marked as expected
failures on future test runs.

Inspired by:
    - https://github.com/pytest-dev/pytest/blob/master/src/_pytest/cacheprovider.py
    - https://github.com/hackebrot/pytest-md/blob/master/src/pytest_md/plugin.py
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import attr
import pytest


# TODO: Guarantee this is opened from pytest's root dir
# (to allow running pytest in a subdirectory)
DEFAULT_QUARANTINE = "quarantine.txt"


def _item_count(nodeids):
    count = len(nodeids)
    return "{} item{}".format(count, "" if count == 1 else "s")


@attr.s(cmp=False)
class SaveQuarantinePlugin(object):
    """Save the list of failing tests to a quarantine file.

    Attributes:
        quarantine_path (str): The path to the quarantine file
        quarantine_ids (Set[int]):
            The ID's of failed tests to write to ``quarantine_path``
    """

    quarantine_path = attr.ib()
    quarantine_ids = attr.ib(init=False, factory=set)

    def pytest_runtest_logreport(self, report):
        """Save the ID of a failed test to the quarantine."""
        if report.failed:
            self.quarantine_ids.add(report.nodeid)

    def pytest_terminal_summary(self, terminalreporter):
        """Display size of quarantine after running tests."""
        terminalreporter.write_sep(
            "-",
            "{} saved to {}".format(
                _item_count(self.quarantine_ids), self.quarantine_path
            ),
        )

    def pytest_sessionfinish(self, session):
        """Write the ID's of quarantined tests to a file.

        Writes an empty file if all tests are passing, to remove previously failed tests
        from the quarantine.
        """
        with open(self.quarantine_path, "w") as f:
            f.writelines(nodeid + "\n" for nodeid in sorted(self.quarantine_ids))


@attr.s(cmp=False)
class QuarantinePlugin(object):
    """Mark each test listed in a quarantine file as xfail.

    Attributes:
        quarantine_path (str): The path to the quarantine file
        verbose (int): The value of pytest's "verbose" config option
        quarantine_ids (Set[int]): The test ID's read from ``quarantine_path``
        marked_ids (Set[int]): The ID's of collected tests marked as xfail
    """

    quarantine_path = attr.ib()
    verbose = attr.ib()
    quarantine_ids = attr.ib(init=False, factory=set)
    marked_ids = attr.ib(init=False, factory=set)

    def pytest_sessionstart(self, session):
        """Read test ID's from a file into the quarantine."""
        try:
            with open(self.quarantine_path) as f:
                self.quarantine_ids = {nodeid.strip() for nodeid in f}
        except IOError as exc:
            raise pytest.UsageError("Could not load quarantine: " + str(exc))

    def pytest_itemcollected(self, item):
        """Mark a test as xfail if its ID is in the quarantine."""
        if item.nodeid in self.quarantine_ids:
            item.add_marker(pytest.mark.xfail(reason="Quarantined"))
            self.marked_ids.add(item.nodeid)

    def pytest_report_collectionfinish(self):
        """Display number of quarantined items before running tests."""
        if self.verbose >= 0:
            return "added mark.xfail to {} of {} from {}".format(
                len(self.marked_ids),
                _item_count(self.quarantine_ids),
                self.quarantine_path,
            )


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
            QuarantinePlugin(quarantine_path, config.getoption("verbose")),
            "quarantine_plugin",
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
