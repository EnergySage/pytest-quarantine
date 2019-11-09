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
def error_and_failure(testdir):
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


def test_no_output_without_options(testdir):
    result = testdir.runpytest()
    assert DEFAULT_QUARANTINE not in result.stdout.str()


@pytest.fixture
def testdir(testdir):
    def _path_exists(path):
        return testdir.tmpdir.join(path).check(exists=True)

    testdir.path_exists = _path_exists

    def _path_has_content(path, content):
        return testdir.tmpdir.join(path).read() == textwrap.dedent(content)

    testdir.path_has_content = _path_has_content

    def _write_path(path, content):
        testdir.tmpdir.join(path).write(textwrap.dedent(content))

    testdir.write_path = _write_path

    return testdir


@pytest.mark.parametrize("quarantine_path", [None, ".quarantine"])
def test_save_failing_tests(quarantine_path, testdir, error_and_failure):
    args = ["--save-quarantine"]
    if quarantine_path:
        args.append(quarantine_path)
    else:
        quarantine_path = DEFAULT_QUARANTINE

    result = testdir.runpytest(*args)

    result.stdout.fnmatch_lines(
        ["*- 2 items saved to {} -*".format(quarantine_path), "=*failed*"]
    )
    result.assert_outcomes(passed=1, failed=1, error=1)
    assert result.ret == EXIT_TESTSFAILED

    assert testdir.path_has_content(
        quarantine_path,
        """\
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """,
    )


def test_no_save_with_passing_tests(testdir):
    quarantine_path = DEFAULT_QUARANTINE

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
    assert quarantine_path not in result.stdout.str()
    assert not testdir.path_exists(quarantine_path)


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
def test_full_quarantine(quarantine_path, testdir, error_and_failure):
    args = ["--quarantine"]
    if quarantine_path:
        args.append(quarantine_path)
    else:
        quarantine_path = DEFAULT_QUARANTINE

    testdir.write_path(
        quarantine_path,
        """\
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """,
    )

    result = testdir.runpytest(*args)

    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 2 of 2 items from {}".format(quarantine_path),
        ]
    )
    result.assert_outcomes(passed=1, xfailed=2)
    assert result.ret == EXIT_OK


def test_partial_quarantine(testdir, error_and_failure):
    quarantine_path = DEFAULT_QUARANTINE

    testdir.write_path(
        quarantine_path,
        """\
        test_failing_tests.py::test_failure
        test_failing_tests.py::test_extra
        """,
    )

    result = testdir.runpytest("--quarantine")

    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 1 of 2 items from {}".format(quarantine_path),
        ]
    )
    result.assert_outcomes(passed=1, error=1, xfailed=1)
    assert result.ret == EXIT_TESTSFAILED


def test_only_extra_quarantine(testdir, error_and_failure):
    quarantine_path = DEFAULT_QUARANTINE

    testdir.write_path(
        quarantine_path,
        """\
        test_failing_tests.py::test_extra
        """,
    )

    result = testdir.runpytest("--quarantine")

    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 0 of 1 item from {}".format(quarantine_path),
        ]
    )
    result.assert_outcomes(passed=1, failed=1, error=1)
    assert result.ret == EXIT_TESTSFAILED


def test_passing_quarantine(testdir, error_and_failure):
    quarantine_path = DEFAULT_QUARANTINE

    testdir.write_path(
        quarantine_path,
        """\
        test_failing_tests.py::test_pass
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """,
    )

    result = testdir.runpytest("--quarantine")

    result.stdout.fnmatch_lines(
        [
            "collected*",
            "added mark.xfail to 3 of 3 items from {}".format(quarantine_path),
        ]
    )
    result.assert_outcomes(xfailed=2, xpassed=1)
    assert result.ret == EXIT_OK
