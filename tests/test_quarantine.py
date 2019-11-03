from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

import pytest


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


@pytest.mark.parametrize("quarantine_path", [None, ".quarantine"])
def test_save_quarantine(quarantine_path, testdir, failing_tests):
    args = ["--save-quarantine"]
    if quarantine_path:
        args.append(quarantine_path)
    else:
        quarantine_path = "quarantine.txt"

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


@pytest.mark.parametrize("quarantine_path", [None, ".quarantine"])
def test_full_quarantine(quarantine_path, testdir, failing_tests):
    args = ["--quarantine"]
    if quarantine_path:
        args.append(quarantine_path)
    else:
        quarantine_path = "quarantine.txt"

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
    testdir.tmpdir.join("quarantine.txt").write(quarantine)

    result = testdir.runpytest("--quarantine")

    result.assert_outcomes(passed=1, error=1, xfailed=1)


def test_missing_quarantine(testdir, failing_tests):
    result = testdir.runpytest("--quarantine")

    result.assert_outcomes(passed=1, failed=1, error=1)
