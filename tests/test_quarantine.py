import pytest


def test_options(testdir):
    result = testdir.runpytest("--help")

    result.stdout.fnmatch_lines(
        ["quarantine:", "*--save-quarantine=*", "*--quarantine=*"]
    )


@pytest.fixture
def failing_tests(testdir):
    testdir.makepyfile(
        """
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

    assert testdir.tmpdir.join("quarantine.txt").read() == (
        "test_save_quarantine.py::test_error\ntest_save_quarantine.py::test_failure\n"
    )


def test_use_quarantine(testdir, failing_tests):
    testdir.tmpdir.join("quarantine.txt").write(
        "test_use_quarantine.py::test_error\ntest_use_quarantine.py::test_failure\n"
    )

    result = testdir.runpytest("--quarantine")

    result.stdout.fnmatch_lines(["quarantine: quarantine.txt"])
    result.assert_outcomes(passed=1, xfailed=2)
