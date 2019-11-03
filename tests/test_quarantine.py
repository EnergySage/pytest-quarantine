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


def test_save_quarantine(testdir, failing_tests):
    result = testdir.runpytest("--save-quarantine")

    result.stdout.fnmatch_lines(["save_quarantine: quarantine.txt"])
    result.assert_outcomes(passed=1, failed=1, error=1)

    quarantine = textwrap.dedent(
        """\
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """
    )

    assert testdir.tmpdir.join("quarantine.txt").read() == quarantine


def test_use_quarantine(testdir, failing_tests):
    quarantine = textwrap.dedent(
        """\
        test_failing_tests.py::test_error
        test_failing_tests.py::test_failure
        """
    )

    testdir.tmpdir.join("quarantine.txt").write(quarantine)

    result = testdir.runpytest("--quarantine")

    result.stdout.fnmatch_lines(["quarantine: quarantine.txt"])
    result.assert_outcomes(passed=1, xfailed=2)
