from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import logging
import os
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


class TestOptions:
    def test_help(self, testdir):
        result = testdir.runpytest("--help")

        result.stdout.fnmatch_lines(
            ["quarantine:", "*--save-quarantine=PATH*", "*--quarantine=PATH*"]
        )

    def test_not_used(self, testdir, error_failed_passed):
        result = testdir.runpytest()

        assert result.ret == EXIT_TESTSFAILED
        assert QUARANTINE_PATH not in result.stdout.str()

    @pytest.mark.parametrize("option", ["--quarantine", "--save-quarantine"])
    def test_required_path(self, option, testdir):
        result = testdir.runpytest(option)

        assert result.ret == EXIT_USAGEERROR
        result.stderr.fnmatch_lines(["*error:*expected one argument"])


class TestSaveQuarantine:
    @pytest.mark.parametrize(
        "quarantine_path", [QUARANTINE_PATH, "reports/quarantine.txt"]
    )
    def test_write_failures(self, quarantine_path, testdir, error_failed_passed):
        result = testdir.runpytest("--save-quarantine", quarantine_path)

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

    def test_dont_write_other_outcomes(self, testdir):
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

    def test_write_empty(self, testdir):
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

    def test_close(self, caplog, testdir):
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

    def test_make_dir_error(self, testdir):
        quarantine_dir = "reports"
        quarantine_path = os.path.join(quarantine_dir, QUARANTINE_PATH)

        # Cause makedirs() to fail by creating a file where the directory would be
        testdir.write_path(quarantine_dir, "")

        result = testdir.runpytest("--save-quarantine", quarantine_path)

        assert result.ret == EXIT_USAGEERROR
        result.stderr.fnmatch_lines(
            ["ERROR: Could not open quarantine:*{}*".format(quarantine_dir)]
        )

    def test_path_error(self, testdir, error_failed_passed):
        # Cause open() to fail by creating a directory where the file should be
        testdir.mkdir(QUARANTINE_PATH)

        result = testdir.runpytest("--save-quarantine", QUARANTINE_PATH)

        assert result.ret == EXIT_USAGEERROR
        result.stderr.fnmatch_lines(
            ["ERROR: Could not open quarantine:*{}*".format(QUARANTINE_PATH)]
        )


class TestUseQuarantine:
    def test_full(self, testdir, error_failed_passed):
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

    def test_partial(self, testdir, error_failed_passed):
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

    def test_only_extra(self, testdir, error_failed_passed):
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

    def test_passing(self, testdir, error_failed_passed):
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

    def test_quiet(self, testdir, error_failed_passed):
        testdir.write_path(
            QUARANTINE_PATH,
            """\
            test_error_failed_passed.py::test_error
            """,
        )

        result = testdir.runpytest("-q", "--quarantine", QUARANTINE_PATH)

        assert QUARANTINE_PATH not in result.stdout.str()

    def test_path_error(self, testdir):
        result = testdir.runpytest("--quarantine", QUARANTINE_PATH)

        assert result.ret == EXIT_USAGEERROR
        result.stderr.fnmatch_lines(
            ["ERROR: Could not open quarantine:*{}*".format(QUARANTINE_PATH)]
        )
