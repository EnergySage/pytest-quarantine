# pytest-quarantine

[![PyPI version](https://img.shields.io/pypi/v/pytest-quarantine.svg)](https://pypi.org/project/pytest-quarantine)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-quarantine.svg)](https://pypi.org/project/pytest-quarantine)
[![Linux build status](https://img.shields.io/travis/com/EnergySage/pytest-quarantine?logo=travis)](https://travis-ci.com/EnergySage/pytest-quarantine)
[![Windows build status](https://img.shields.io/appveyor/ci/EnergySage/pytest-quarantine?logo=appveyor)](https://ci.appveyor.com/project/EnergySage/pytest-quarantine)
[![Test coverage](https://img.shields.io/codecov/c/github/EnergySage/pytest-quarantine?logo=codecov)](https://codecov.io/gh/EnergySage/pytest-quarantine)

A plugin for [pytest](https://github.com/pytest-dev/pytest) to manage expected test failures.

## Features

Save the list of failing tests, so that they can be automatically marked as expected failures on future test runs.

### Why?

You've got a test suite; nicely done! Unfortunately, for completely understandable reasons, a lot of the tests are failing. Someday, you and/or your team will get those tests to pass. For now, though, what you really want is to draw a line in the sand and avoid new test failures. Unfortunately, it's hard to tell when those are introduced because the test suite is already failing. You could get the test suite to pass by adding `pytest.mark.xfail` to the existing failures, but there are *so many* of them.

With this plugin, you can save all of current failures to a file (the quarantine). On future test runs, this plugin will automatically apply `pytest.mark.xfail` to the quarantined tests. Then, the test suite will pass, and any new failures will cause it to fail.

## Requirements

- Python 2.7 or 3.5+
- pytest 4.6 or newer

## Installation

Via [pip](https://pypi.org/project/pip/) from [PyPI](https://pypi.org/project/pytest-quarantine):

```
$ pip install pytest-quarantine
```

## Usage

Run your test suite and save the failing tests to `quarantine.txt`:

```
$ pytest --save-quarantine

= 629 failed, 719 passed, 32 error in 312.56 seconds =
```

Add `quarantine.txt` to your version control system.

Run your test suite with the quarantined tests marked as expected failures:

```
$ pytest --quarantine

= 719 passed, 661 xfailed in 300.51 seconds =
```

When the expected failures eventually pass, they can be removed manually from `quarantine.txt`, or automatically using `--save-quarantine`. Note that the latter will overwrite the contents of the quarantine, so it's best to only use it when running the entire test suite.

The default `quarantine.txt` can be changed by an optional argument (for example, if test failures differ between environments, or for multiple test suites):

```
$ pytest --save-quarantine=quarantine-py3.txt

$ pytest --quarantine=quarantine-py3.txt
```

## Getting help

Please submit questions, bug reports, and feature requests in the [issue tracker](https://github.com/energysage/pytest-quarantine/issues).

## Contributing

Improvements to the code and documentation are greatly appreciated. See [How to contribute](https://github.com/energysage/pytest-quarantine/blob/master/CONTRIBUTING.md) for details.

## Code of conduct

Everyone interacting with this project is expected to follow the [Contributor Covenant](https://github.com/energysage/pytest-quarantine/blob/master/CODE_OF_CONDUCT.md).

## License

Distributed under the terms of the [MIT](http://opensource.org/licenses/MIT) license.

## Acknowledgements

This project was initially generated with [Cookiecutter](https://github.com/audreyr/cookiecutter) using the [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin) template. The layout and tooling has been heavily modified since then, but it was very helpful to start.
