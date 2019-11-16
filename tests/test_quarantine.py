from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

import pytest

try:
    EXIT_OK = pytest.ExitCode.OK
    EXIT_TESTSFAILED = pytest.ExitCode.TESTS_FAILED
    EXIT_USAGEERROR = pytest.ExitCode.USAGE_ERROR
except AttributeError:
    # ExitCode was introduced in pytest 5.0.0. As long as we support pytest 4.6 (for
    # Python 2), use the private constants for readability.
    from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_USAGEERROR  # noqa: F401

from pytest_quarantine import DEFAULT_QUARANTINE


def test_default_file():
    assert DEFAULT_QUARANTINE == "quarantine.txt"


def test_options_in_help(testdir):
    result = testdir.runpytest("--help")

    result.stdout.fnmatch_lines(
        ["quarantine:", "*--save-quarantine=PATH", "*--quarantine=PATH*"]
    )


@pytest.mark.parametrize("option", ["--quarantine", "--save-quarantine"])
def test_options_require_path(option, testdir):
    result = testdir.runpytest(option)

    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(["*error:*expected one argument"])


@pytest.fixture
def error_failed_passed(testdir):
    """Create test_error_failed_passed.py with one test for each outcome."""
    return testdir.makepyfile(
        test_error_failed_passed="""\
        import pytest

        @pytest.fixture
        def error():
            assert False

        def test_error(error):
            assert True

        def test_failed():
            assert False

        def test_passed():
            assert True
        """
    )


def test_no_output_without_options(testdir):
    result = testdir.runpytest()
    assert DEFAULT_QUARANTINE not in result.stdout.str()


@pytest.fixture
def testdir(testdir):
    """Return default testdir fixture with additional helper methods."""

    def _path_has_content(path, content):
        return testdir.tmpdir.join(path).read() == textwrap.dedent(content)

    testdir.path_has_content = _path_has_content

    def _write_path(path, content):
        testdir.tmpdir.join(path).write(textwrap.dedent(content))

    testdir.write_path = _write_path

    return testdir


@pytest.mark.parametrize("quarantine_path", [DEFAULT_QUARANTINE, ".quarantine"])
def test_save_failing_tests(quarantine_path, testdir, error_failed_passed):
    args = ["--save-quarantine", quarantine_path]
    result = testdir.runpytest(*args)

    assert result.ret == EXIT_TESTSFAILED
    result.assert_outcomes(passed=1, failed=1, error=1)
    result.stdout.fnmatch_lines(
        ["*- 2 items saved to {} -*".format(quarantine_path), "=*failed*"]
    )

    assert testdir.path_has_content(
        quarantine_path,
        """\
        test_error_failed_passed.py::test_error
        test_error_failed_passed.py::test_failed
        """,
    )


def test_dont_save_other_outcomes(testdir):
    quarantine_path = DEFAULT_QUARANTINE
    args = ["--save-quarantine", quarantine_path]

    testdir.makepyfile(
        """\
        import pytest

        def test_passed():
            assert True

        @pytest.mark.skip
        def test_skipped():
            assert False

        @pytest.mark.xfail
        def test_xfailed():
            assert False

        @pytest.mark.xfail
        def test_xpassed():
            assert True
        """
    )

    result = testdir.runpytest(*args)

    assert result.ret == EXIT_OK
    result.assert_outcomes(passed=1, skipped=1, xpassed=1, xfailed=1)
    result.stdout.fnmatch_lines(
        ["*- 0 items saved to {} -*".format(quarantine_path), "=*skipped*"]
    )

    assert testdir.path_has_content(quarantine_path, "")


def test_save_empty_quarantine(testdir):
    quarantine_path = DEFAULT_QUARANTINE
    args = ["--save-quarantine", quarantine_path]

    testdir.makepyfile(
        test_xpassed="""\
        def test_passed():
            assert True
        """
    )

    testdir.write_path(
        quarantine_path,
        """\
        test_xpassed.py::test_passed
        """,
    )

    result = testdir.runpytest(*args)

    assert result.ret == EXIT_OK
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(
        ["*- 0 items saved to {} -*".format(quarantine_path), "=*passed*"]
    )

    assert testdir.path_has_content(quarantine_path, "")


@pytest.mark.parametrize("quarantine_path", [DEFAULT_QUARANTINE, ".quarantine"])
def test_missing_quarantine(quarantine_path, testdir):
    args = ["--quarantine", quarantine_path]

    result = testdir.runpytest(*args)

    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        ["ERROR: Could not load quarantine:*'{}'".format(quarantine_path)]
    )


@pytest.mark.parametrize("quarantine_path", [DEFAULT_QUARANTINE, ".quarantine"])
def test_full_quarantine(quarantine_path, testdir, error_failed_passed):
    args = ["--quarantine", quarantine_path]

    testdir.write_path(
        quarantine_path,
        """\
        test_error_failed_passed.py::test_error
        test_error_failed_passed.py::test_failed
        """,
    )

    result = testdir.runpytest(*args)

    assert result.ret == EXIT_OK
    result.assert_outcomes(passed=1, xfailed=2)
    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 2 of 2 items from {}".format(quarantine_path),
        ]
    )


def test_partial_quarantine(testdir, error_failed_passed):
    quarantine_path = DEFAULT_QUARANTINE
    args = ["--quarantine", quarantine_path]

    testdir.write_path(
        quarantine_path,
        """\
        test_error_failed_passed.py::test_failed
        test_error_failed_passed.py::test_extra
        """,
    )

    result = testdir.runpytest(*args)

    assert result.ret == EXIT_TESTSFAILED
    result.assert_outcomes(passed=1, error=1, xfailed=1)
    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 1 of 2 items from {}".format(quarantine_path),
        ]
    )


def test_only_extra_quarantine(testdir, error_failed_passed):
    quarantine_path = DEFAULT_QUARANTINE
    args = ["--quarantine", quarantine_path]

    testdir.write_path(
        quarantine_path,
        """\
        test_error_failed_passed.py::test_extra
        """,
    )

    result = testdir.runpytest(*args)

    assert result.ret == EXIT_TESTSFAILED
    result.assert_outcomes(passed=1, failed=1, error=1)
    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 0 of 1 item from {}".format(quarantine_path),
        ]
    )


def test_passing_quarantine(testdir, error_failed_passed):
    quarantine_path = DEFAULT_QUARANTINE
    args = ["--quarantine", quarantine_path]

    testdir.write_path(
        quarantine_path,
        """\
        test_error_failed_passed.py::test_error
        test_error_failed_passed.py::test_failed
        test_error_failed_passed.py::test_passed
        """,
    )

    result = testdir.runpytest(*args)

    assert result.ret == EXIT_OK
    result.assert_outcomes(xfailed=2, xpassed=1)
    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 3 of 3 items from {}".format(quarantine_path),
        ]
    )


def test_no_report_with_quiet_option(testdir, error_failed_passed):
    quarantine_path = DEFAULT_QUARANTINE
    args = ["-q", "--quarantine", quarantine_path]

    testdir.write_path(
        quarantine_path,
        """\
        test_error_failed_passed.py::test_error
        """,
    )

    result = testdir.runpytest(*args)

    assert quarantine_path not in result.stdout.str()
