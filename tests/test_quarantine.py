from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import logging
import textwrap

import pytest

try:
    EXIT_OK = pytest.ExitCode.OK
    EXIT_TESTSFAILED = pytest.ExitCode.TESTS_FAILED
    EXIT_INTERNALERROR = pytest.ExitCode.INTERNAL_ERROR
    EXIT_USAGEERROR = pytest.ExitCode.USAGE_ERROR
except AttributeError:
    # ExitCode was introduced in pytest 5.0.0. As long as we support pytest 4.6 (for
    # Python 2), use the private constants for readability.
    from _pytest.main import (
        EXIT_OK,
        EXIT_TESTSFAILED,
        EXIT_INTERNALERROR,
        EXIT_USAGEERROR,
    )

QUARANTINE_PATH = "quarantine.txt"


def test_options_in_help(testdir):
    result = testdir.runpytest("--help")

    result.stdout.fnmatch_lines(
        ["quarantine:", "*--save-quarantine=PATH*", "*--quarantine=PATH*"]
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


def test_no_output_without_options(testdir, error_failed_passed):
    result = testdir.runpytest()

    assert result.ret == EXIT_TESTSFAILED
    assert QUARANTINE_PATH not in result.stdout.str()


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


def test_save_failing_tests(testdir, error_failed_passed):
    result = testdir.runpytest("--save-quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_TESTSFAILED
    result.assert_outcomes(passed=1, failed=1, error=1)
    result.stdout.fnmatch_lines(
        ["*- 2 items saved to {} -*".format(QUARANTINE_PATH), "=*failed*"]
    )

    assert testdir.path_has_content(
        QUARANTINE_PATH,
        """\
        test_error_failed_passed.py::test_error
        test_error_failed_passed.py::test_failed
        """,
    )


def test_dont_save_other_outcomes(testdir):
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

    result = testdir.runpytest("--save-quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_OK
    result.assert_outcomes(passed=1, skipped=1, xpassed=1, xfailed=1)
    result.stdout.fnmatch_lines(
        ["*- 0 items saved to {} -*".format(QUARANTINE_PATH), "=*skipped*"]
    )

    assert testdir.path_has_content(QUARANTINE_PATH, "")


def test_save_empty_quarantine(testdir):
    testdir.makepyfile(
        test_xpassed="""\
        def test_passed():
            assert True
        """
    )

    testdir.write_path(
        QUARANTINE_PATH,
        """\
        test_xpassed.py::test_passed
        """,
    )

    result = testdir.runpytest("--save-quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_OK
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(
        ["*- 0 items saved to {} -*".format(QUARANTINE_PATH), "=*passed*"]
    )

    assert testdir.path_has_content(QUARANTINE_PATH, "")


def test_save_always_closes_quarantine(caplog, testdir):
    caplog.set_level(logging.DEBUG)

    testdir.makeconftest(
        """\
        def pytest_runtestloop():
            raise Exception()
        """
    )

    result = testdir.runpytest("--save-quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_INTERNALERROR
    assert "Closed " + QUARANTINE_PATH in caplog.text


def test_save_dir_error(testdir, error_failed_passed):
    testdir.mkdir("quarantine")

    result = testdir.runpytest("--save-quarantine", "quarantine")

    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(["*error:*file path*"])


def test_missing_quarantine(testdir):
    result = testdir.runpytest("--quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        ["ERROR: Could not load quarantine:*'{}'".format(QUARANTINE_PATH)]
    )


def test_full_quarantine(testdir, error_failed_passed):
    testdir.write_path(
        QUARANTINE_PATH,
        """\
        test_error_failed_passed.py::test_error
        test_error_failed_passed.py::test_failed
        """,
    )

    result = testdir.runpytest("--quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_OK
    result.assert_outcomes(passed=1, xfailed=2)
    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 2 of 2 items from {}".format(QUARANTINE_PATH),
        ]
    )


def test_partial_quarantine(testdir, error_failed_passed):
    testdir.write_path(
        QUARANTINE_PATH,
        """\
        test_error_failed_passed.py::test_failed
        test_error_failed_passed.py::test_extra
        """,
    )

    result = testdir.runpytest("--quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_TESTSFAILED
    result.assert_outcomes(passed=1, error=1, xfailed=1)
    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 1 of 2 items from {}".format(QUARANTINE_PATH),
        ]
    )


def test_only_extra_quarantine(testdir, error_failed_passed):
    testdir.write_path(
        QUARANTINE_PATH,
        """\
        test_error_failed_passed.py::test_extra
        """,
    )

    result = testdir.runpytest("--quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_TESTSFAILED
    result.assert_outcomes(passed=1, failed=1, error=1)
    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 0 of 1 item from {}".format(QUARANTINE_PATH),
        ]
    )


def test_passing_quarantine(testdir, error_failed_passed):
    testdir.write_path(
        QUARANTINE_PATH,
        """\
        test_error_failed_passed.py::test_error
        test_error_failed_passed.py::test_failed
        test_error_failed_passed.py::test_passed
        """,
    )

    result = testdir.runpytest("--quarantine", QUARANTINE_PATH)

    assert result.ret == EXIT_OK
    result.assert_outcomes(xfailed=2, xpassed=1)
    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 3 of 3 items from {}".format(QUARANTINE_PATH),
        ]
    )


def test_no_report_with_quiet_option(testdir, error_failed_passed):
    testdir.write_path(
        QUARANTINE_PATH,
        """\
        test_error_failed_passed.py::test_error
        """,
    )

    result = testdir.runpytest("-q", "--quarantine", QUARANTINE_PATH)

    assert QUARANTINE_PATH not in result.stdout.str()
