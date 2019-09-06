import pytest


def pytest_addoption(parser):
    """Add the `--foo` command-line option."""
    group = parser.getgroup("quarantine")
    group.addoption(
        "--foo",
        action="store",
        dest="dest_foo",
        default="2019",
        help='Set the value for the fixture "bar".',
    )

    parser.addini("HELLO", "Dummy pytest.ini setting")


@pytest.fixture
def bar(request):
    """Return the value of the `foo` option."""
    return request.config.option.dest_foo
