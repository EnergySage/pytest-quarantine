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


def test_options(testdir):
    result = testdir.runpytest("--help")

    result.stdout.fnmatch_lines(
        ["quarantine:", "*--save-quarantine=*", "*--quarantine=*"]
    )


@pytest.fixture
def failing_tests(testdir):
    return testdir.makepyfile(
        test_failing_tests="""\
        import pytest

        @pytest.fixture
        def error():
            assert False

        def test_error(error):
            assert True

        def test_failure():
            assert False

        def test_pass():
            assert True
        """
    )


def test_no_report_header_without_options(testdir):
    result = testdir.runpytest()
    assert "quarantine: " not in result.outlines


@pytest.mark.parametrize("quarantine_path", [None, ".quarantine"])
def test_save_failing_tests(quarantine_path, testdir, failing_tests):
    args = ["--save-quarantine"]
    if quarantine_path:
        args.append(quarantine_path)
    else:
        quarantine_path = DEFAULT_QUARANTINE

    result = testdir.runpytest(*args)

    result.stdout.fnmatch_lines(
        ["save_quarantine: {}".format(quarantine_path), "collected*"]
    )
    result.assert_outcomes(passed=1, failed=1, error=1)
    assert result.ret == EXIT_TESTSFAILED

    quarantine = textwrap.dedent(
        """\
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """
    )
    assert testdir.tmpdir.join(quarantine_path).read() == quarantine


def test_no_save_with_passing_tests(testdir):
    testdir.makepyfile(
        """\
        import pytest

        def test_pass():
            assert True
        """
    )

    result = testdir.runpytest("--save-quarantine")

    result.assert_outcomes(passed=1)
    assert result.ret == EXIT_OK
    assert testdir.tmpdir.join(DEFAULT_QUARANTINE).check(exists=False)


@pytest.mark.parametrize("quarantine_path", [None, ".quarantine"])
def test_missing_quarantine(quarantine_path, testdir):
    args = ["--quarantine"]
    if quarantine_path:
        args.append(quarantine_path)
    else:
        quarantine_path = DEFAULT_QUARANTINE

    result = testdir.runpytest(*args)

    result.stderr.fnmatch_lines(
        ["ERROR: Could not load quarantine:*'{}'".format(quarantine_path)]
    )
    assert result.ret == EXIT_USAGEERROR


@pytest.mark.parametrize("quarantine_path", [None, ".quarantine"])
def test_full_quarantine(quarantine_path, testdir, failing_tests):
    args = ["--quarantine"]
    if quarantine_path:
        args.append(quarantine_path)
    else:
        quarantine_path = DEFAULT_QUARANTINE

    quarantine = textwrap.dedent(
        """\
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """
    )
    testdir.tmpdir.join(quarantine_path).write(quarantine)

    result = testdir.runpytest(*args)

    result.stdout.fnmatch_lines(
        ["collected*", "quarantine: 2 tests in {}".format(quarantine_path)]
    )
    result.assert_outcomes(passed=1, xfailed=2)
    assert result.ret == EXIT_OK


def test_partial_quarantine(testdir, failing_tests):
    quarantine_path = DEFAULT_QUARANTINE

    quarantine = textwrap.dedent(
        """\
        test_failing_tests.py::test_failure
        """
    )
    testdir.tmpdir.join(quarantine_path).write(quarantine)

    result = testdir.runpytest("--quarantine")

    result.stdout.fnmatch_lines(
        ["collected*", "quarantine: 1 test in {}".format(quarantine_path)]
    )
    result.assert_outcomes(passed=1, error=1, xfailed=1)
    assert result.ret == EXIT_TESTSFAILED


def test_passing_quarantine(testdir, failing_tests):
    quarantine_path = DEFAULT_QUARANTINE

    quarantine = textwrap.dedent(
        """\
        test_failing_tests.py::test_pass
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """
    )
    testdir.tmpdir.join(quarantine_path).write(quarantine)

    result = testdir.runpytest("--quarantine")

    result.assert_outcomes(xfailed=2, xpassed=1)
    assert result.ret == EXIT_OK
