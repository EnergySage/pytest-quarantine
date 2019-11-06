from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

import pytest
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
    assert "quarantine: " not in result.stdout.str()


@pytest.mark.parametrize("quarantine_path", [None, ".quarantine"])
def test_save_failing_tests(quarantine_path, testdir, failing_tests):
    args = ["--save-quarantine"]
    if quarantine_path:
        args.append(quarantine_path)
    else:
        quarantine_path = DEFAULT_QUARANTINE

    result = testdir.runpytest(*args)

    result.stdout.fnmatch_lines(["save_quarantine: {}".format(quarantine_path)])
    result.assert_outcomes(passed=1, failed=1, error=1)

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
    assert testdir.tmpdir.join(DEFAULT_QUARANTINE).check(exists=False)


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

    result.stdout.fnmatch_lines(["quarantine: {}".format(quarantine_path)])
    result.assert_outcomes(passed=1, xfailed=2)


def test_partial_quarantine(testdir, failing_tests):
    quarantine = textwrap.dedent(
        """\
        test_failing_tests.py::test_failure
        """
    )
    testdir.tmpdir.join(DEFAULT_QUARANTINE).write(quarantine)

    result = testdir.runpytest("--quarantine")

    result.assert_outcomes(passed=1, error=1, xfailed=1)


def test_passing_quarantine(testdir, failing_tests):
    quarantine = textwrap.dedent(
        """\
        test_failing_tests.py::test_pass
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """
    )
    testdir.tmpdir.join(DEFAULT_QUARANTINE).write(quarantine)

    result = testdir.runpytest("--quarantine")

    result.assert_outcomes(xfailed=2, xpassed=1)


def test_missing_quarantine(testdir, failing_tests):
    result = testdir.runpytest("--quarantine")

    result.assert_outcomes(passed=1, failed=1, error=1)
