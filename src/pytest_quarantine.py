import pytest


class QuarantinePlugin(object):
    """Save a list of failing tests to be marked as xfail on future test runs."""

    # TODO: Guarantee this is opened from pytest's root dir
    DEFAULT_QUARANTINE = "quarantine.txt"

    def __init__(self, config):
        self.quarantine = config.getoption("quarantine")
        self.save_quarantine = config.getoption("save_quarantine")
        self.nodeids = set()

    def pytest_report_header(self, config):
        """Display configuration at runtime."""
        options = [
            (option, getattr(self, option))
            for option in ["quarantine", "save_quarantine"]
        ]
        return ["{}: {}".format(option, value) for option, value in options if value]

    def pytest_runtestloop(self, session):
        """Read the ID's of quarantined tests from a file."""
        if not self.quarantine:
            return

        with open(self.quarantine) as f:
            for nodeid in f:
                self.nodeids.add(nodeid.strip())

    def pytest_runtest_setup(self, item):
        """Mark a test as `xfail` if its ID is in the quarantine."""
        if self.quarantine and item.nodeid in self.nodeids:
            item.add_marker(pytest.mark.xfail(reason="Quarantined"))

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


def pytest_addoption(parser):
    """Add command line options to the 'quarantine' group."""
    group = parser.getgroup("quarantine")

    group.addoption(
        "--save-quarantine",
        nargs="?",
        const=QuarantinePlugin.DEFAULT_QUARANTINE,
        metavar="PATH",
        help="Write failing tests to %(metavar)s (default: %(const)s)",
    )

    group.addoption(
        "--quarantine",
        nargs="?",
        const=QuarantinePlugin.DEFAULT_QUARANTINE,
        metavar="PATH",
        help="Mark tests listed in %(metavar)s with `xfail` (default: %(const)s)",
    )


# TODO: ValueError: Plugin already registered: quarantine
# def pytest_configure(config):
#     """Register the plugin."""
#     config.pluginmanager.register(QuarantinePlugin(config), "quarantine")
